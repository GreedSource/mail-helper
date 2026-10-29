from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class MailConfig:
    server: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    default_sender: str | None = None
    use_tls: bool = True
    use_ssl: bool = False
    timeout: float = 30.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> MailConfig:
        values = os.environ if environ is None else environ
        server = values.get("MAIL_SERVER")
        if not server:
            raise ValueError("MAIL_SERVER must be set")

        return cls(
            server=server,
            port=int(values.get("MAIL_PORT", "587")),
            username=values.get("MAIL_USERNAME") or None,
            password=values.get("MAIL_PASSWORD") or None,
            default_sender=values.get("MAIL_DEFAULT_SENDER") or None,
            use_tls=_as_bool(values.get("MAIL_USE_TLS", "true")),
            use_ssl=_as_bool(values.get("MAIL_USE_SSL", "false")),
            timeout=float(values.get("MAIL_TIMEOUT", "30")),
        )


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
