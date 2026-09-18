from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast
from uuid import uuid4

from dossier_mcp.domain import (
    CLIENTS,
    DIRECTORY_FIELDS,
    SENSITIVE_CLIENT_FIELDS,
    schema_fingerprint,
)
from dossier_mcp.errors import TeableFailure, ToolError
from dossier_mcp.settings import Settings
from dossier_mcp.teable import TeableClient


class DossierService:
    """Domain operations, deliberately limited to the approved read surface."""

    def __init__(self, client: TeableClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def find_clients(self, query: str, limit: int = 10) -> dict[str, Any]:
        correlation_id = str(uuid4())
        if not query.strip():
            return ToolError("invalid_input", "query must not be empty", correlation_id).response()
        if not 1 <= limit <= 25:
            return ToolError("invalid_input", "limit must be between 1 and 25", correlation_id).response()
        try:
            matches = await self._matching_clients(query.strip(), limit)
        except TeableFailure as error:
            return ToolError(error.category, str(error), correlation_id).response()
        return {"ok": True, "correlation_id": correlation_id, "clients": matches}

    async def get_client_dossier(self, client_record_id: str, include_sensitive: bool = False) -> dict[str, Any]:
        correlation_id = str(uuid4())
        if not client_record_id.startswith("rec"):
            return ToolError("invalid_input", "client_record_id must be a Teable record ID", correlation_id).response()
        if include_sensitive and not self._settings.allow_pii_read:
            return ToolError(
                "authorization_denied",
                "This environment does not permit sensitive client fields",
                correlation_id,
            ).response()
        projection: Sequence[str] = DIRECTORY_FIELDS
        if include_sensitive:
            projection = (*projection, *SENSITIVE_CLIENT_FIELDS)
        try:
            record = await self._find_client(client_record_id, projection)
        except TeableFailure as error:
            return ToolError(error.category, str(error), correlation_id).response()
        if record is None:
            return ToolError("not_found", "Client record does not exist", correlation_id).response()
        return {
            "ok": True,
            "correlation_id": correlation_id,
            "client": self._public_client(record, projection),
            "sensitive_fields_included": include_sensitive,
        }

    async def _matching_clients(self, query: str, limit: int) -> list[dict[str, Any]]:
        normalized_query = query.casefold()
        matches: list[dict[str, Any]] = []
        skip = 0
        while True:
            records = await self._client.list_records(CLIENTS.id, DIRECTORY_FIELDS, skip=skip)
            for record in records:
                title = self._fields(record).get(DIRECTORY_FIELDS[0])
                if isinstance(title, str) and normalized_query in title.casefold():
                    matches.append(self._public_client(record, DIRECTORY_FIELDS))
                    if len(matches) == limit:
                        return matches
            if len(records) < 100:
                return matches
            skip += len(records)

    async def _find_client(self, record_id: str, projection: Sequence[str]) -> dict[str, Any] | None:
        skip = 0
        while True:
            records = await self._client.list_records(CLIENTS.id, projection, skip=skip)
            for record in records:
                if record.get("id") == record_id:
                    return record
            if len(records) < 100:
                return None
            skip += len(records)

    @staticmethod
    def _fields(record: dict[str, Any]) -> dict[str, Any]:
        fields = record.get("fields")
        return cast(dict[str, Any], fields) if isinstance(fields, dict) else {}

    @classmethod
    def _public_client(cls, record: dict[str, Any], projection: Sequence[str]) -> dict[str, Any]:
        record_id = record.get("id")
        fields = cls._fields(record)
        return {
            "record_id": record_id if isinstance(record_id, str) else None,
            "fields": {
                CLIENTS.field(field_id).label: fields.get(field_id) for field_id in projection if field_id in fields
            },
        }

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "mode": self._settings.mode,
            "write_operations": "disabled_pending_owner_policy",
            "sensitive_client_read": self._settings.allow_pii_read,
            "schema_snapshot_fingerprint": schema_fingerprint(),
            "schema_snapshot_is_runtime_verified": False,
        }
