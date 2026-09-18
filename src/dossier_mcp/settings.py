from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, cast

Mode = Literal["development", "demo"]


@dataclass(frozen=True)
class Settings:
    endpoint: str
    token: str
    mode: Mode
    allow_pii_read: bool

    @classmethod
    def from_environment(cls) -> Settings:
        mode = os.environ.get("DOSSIER_MODE")
        if mode not in {"development", "demo"}:
            raise ValueError("DOSSIER_MODE must be development or demo")
        token = os.environ.get("TEABLE_TOKEN")
        if not token:
            raise ValueError("TEABLE_TOKEN is required")
        endpoint = os.environ.get("TEABLE_ENDPOINT", "https://app.teable.ai").rstrip("/")
        if not endpoint.startswith("https://"):
            raise ValueError("TEABLE_ENDPOINT must use HTTPS")
        return cls(
            endpoint=endpoint,
            token=token,
            mode=cast(Mode, mode),
            allow_pii_read=os.environ.get("DOSSIER_ALLOW_PII_READ") == "1",
        )
