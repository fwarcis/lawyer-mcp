from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ToolError:
    category: str
    message: str
    correlation_id: str

    def response(self) -> dict[str, Any]:
        return {"ok": False, "error": asdict(self)}


class TeableFailure(Exception):
    """An upstream failure stripped of response bodies and credentials."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category
