from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any, cast

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from dossier_mcp.errors import TeableFailure
from dossier_mcp.settings import Settings


class TeableClient:
    """Small adapter for the documented, read-only Teable record endpoint."""

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._settings = settings
        self._transport = transport
        self._last_request = 0.0
        self._rate_lock = asyncio.Lock()

    async def list_records(
        self, table_id: str, projection: Sequence[str], *, skip: int = 0, take: int = 100
    ) -> list[dict[str, Any]]:
        if not 0 <= skip:
            raise ValueError("skip must not be negative")
        if not 1 <= take <= 100:
            raise ValueError("take must be between 1 and 100")
        response = await self._get(
            f"/api/table/{table_id}/record",
            params={
                "fieldKeyType": "id",
                "cellFormat": "json",
                "projection": list(projection),
                "skip": skip,
                "take": take,
            },
        )
        payload = self._json_object(response)
        records: object = payload.get("records")
        if not isinstance(records, list):
            raise TeableFailure("unexpected_upstream", "Teable returned an unexpected records response")
        return cast(list[dict[str, Any]], records)

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=0.2, max=2),
        reraise=True,
    )
    async def _get(self, path: str, *, params: dict[str, Any]) -> httpx.Response:
        await self._limit_rate()
        try:
            async with httpx.AsyncClient(
                base_url=self._settings.endpoint,
                headers={"Authorization": f"Bearer {self._settings.token}"},
                timeout=httpx.Timeout(15.0),
                transport=self._transport,
            ) as client:
                response = await client.get(path, params=params)
        except httpx.TransportError:
            raise
        if response.status_code in {401, 403}:
            raise TeableFailure("authorization_denied", "Teable denied this request")
        if response.status_code == 429:
            raise TeableFailure("rate_limited", "Teable rate limit reached; retry later")
        if response.status_code >= 500:
            raise TeableFailure("retryable_upstream", "Teable is temporarily unavailable")
        if response.status_code >= 400:
            raise TeableFailure("upstream_failure", "Teable rejected the request")
        return response

    async def _limit_rate(self) -> None:
        async with self._rate_lock:
            loop = asyncio.get_running_loop()
            wait_for = self._last_request + 0.1 - loop.time()
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            self._last_request = loop.time()

    @staticmethod
    def _json_object(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as error:
            raise TeableFailure("unexpected_upstream", "Teable returned invalid JSON") from error
        if not isinstance(payload, dict):
            raise TeableFailure("unexpected_upstream", "Teable returned an unexpected response")
        return cast(dict[str, Any], payload)
