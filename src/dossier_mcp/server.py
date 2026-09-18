from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from dossier_mcp.domain import MINIMUM_FIELD_PROPOSAL
from dossier_mcp.safe_service import DossierService
from dossier_mcp.settings import Settings
from dossier_mcp.teable import TeableClient


def create_server(service: DossierService) -> MCPServer:
    server = MCPServer("dossier")

    @server.tool()
    def dossier_status() -> dict[str, Any]:
        """Return enabled capabilities and safety status without reading Teable records."""
        return service.status()

    @server.tool()
    def minimum_create_field_proposal() -> dict[str, Any]:
        """Return the proposed smallest field set; it is not an approved write policy."""
        return {
            "ok": True,
            "status": "owner_approval_required",
            "proposal": MINIMUM_FIELD_PROPOSAL,
            "note": "Business-required fields are undefined in the domain contract; creation is disabled.",
        }

    @server.tool()
    async def find_clients(query: str, limit: int = 10) -> dict[str, Any]:
        """Find client directory entries by name without reading contact details or notes."""
        return await service.find_clients(query, limit)

    @server.tool()
    async def get_client_dossier(client_record_id: str, include_sensitive: bool = False) -> dict[str, Any]:
        """Get a client by canonical record ID; sensitive fields require environment permission."""
        return await service.get_client_dossier(client_record_id, include_sensitive)

    return server


def main() -> None:
    settings = Settings.from_environment()
    server = create_server(DossierService(TeableClient(settings), settings))
    server.run()
