from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from dossier_mcp.domain import CLIENTS, DIRECTORY_FIELDS
from dossier_mcp.safe_service import DossierService
from dossier_mcp.settings import Settings
from dossier_mcp.teable import TeableClient


class FakeClient(TeableClient):
    def __init__(self, pages: list[list[dict[str, Any]]]) -> None:
        self.pages = pages
        self.requests: list[tuple[str, tuple[str, ...], int]] = []

    async def list_records(
        self, table_id: str, projection: Sequence[str], *, skip: int = 0, take: int = 100
    ) -> list[dict[str, Any]]:
        self.requests.append((table_id, tuple(projection), skip))
        page = skip // 100
        return self.pages[page] if page < len(self.pages) else []


def settings(*, allow_pii_read: bool = False) -> Settings:
    return Settings("https://example.test", "secret", "development", allow_pii_read)


def record(record_id: str, name: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "fields": {
            DIRECTORY_FIELDS[0]: name,
            DIRECTORY_FIELDS[1]: "Активный",
        },
    }


@pytest.mark.asyncio
async def test_find_clients_uses_allowlisted_projection_and_pages() -> None:
    client = FakeClient([[record("rec1", "Первый") for _ in range(100)], [record("rec2", "Анна")]])
    service = DossierService(client, settings())

    result = await service.find_clients("анна")

    assert result["ok"] is True
    assert result["clients"][0]["record_id"] == "rec2"
    assert client.requests == [
        (CLIENTS.id, DIRECTORY_FIELDS, 0),
        (CLIENTS.id, DIRECTORY_FIELDS, 100),
    ]


@pytest.mark.asyncio
async def test_sensitive_read_is_denied_before_teable_request() -> None:
    client = FakeClient([])
    service = DossierService(client, settings())

    result = await service.get_client_dossier("rec1", include_sensitive=True)

    assert result["error"]["category"] == "authorization_denied"
    assert client.requests == []


@pytest.mark.asyncio
async def test_client_lookup_pages_until_the_record_is_found() -> None:
    client = FakeClient([[record("rec1", "Первый") for _ in range(100)], [record("rec2", "Анна")]])
    service = DossierService(client, settings())

    result = await service.get_client_dossier("rec2")

    assert result["ok"] is True
    assert result["client"]["record_id"] == "rec2"
    assert [request[2] for request in client.requests] == [0, 100]
