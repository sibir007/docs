"""Application configuration loaded from environment variables and CLI values."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def default_hosts_path() -> Path:
    if sys.platform.startswith("win"):
        return Path(r"C:\Windows\System32\drivers\etc\hosts")
    return Path("/etc/hosts")


@dataclass(frozen=True, slots=True)
class AppConfig:
    base_dir: Path
    sites_dir: Path
    bind_host: str = "127.0.0.1"
    preferred_port: int = 8080
    open_browser: bool = True
    log_level: str = "INFO"
    hosts_path: Path = field(default_factory=default_hosts_path)

    @classmethod
    def from_environment(
        cls,
        *,
        bind_host: str | None = None,
        preferred_port: int | None = None,
        sites_dir: Path | None = None,
        open_browser: bool | None = None,
        log_level: str | None = None,
        hosts_path: Path | None = None,
    ) -> AppConfig:
        base_dir = Path(__file__).resolve().parents[2]
        configured_sites_dir = Path(os.getenv("SITES_DIR", str(base_dir / "sites")))
        port = int(os.getenv("PORT", "8080"))
        configured_bind_host = os.getenv("HOST", "127.0.0.1")
        configured_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        config = cls(
            base_dir=base_dir,
            sites_dir=(sites_dir or configured_sites_dir).expanduser().resolve(),
            bind_host=bind_host if bind_host is not None else configured_bind_host,
            preferred_port=preferred_port if preferred_port is not None else port,
            open_browser=(
                open_browser
                if open_browser is not None
                else _env_bool("OPEN_BROWSER", True)
            ),
            log_level=log_level.upper() if log_level is not None else configured_log_level,
            hosts_path=hosts_path or default_hosts_path(),
        )
        if not 0 <= config.preferred_port <= 65535:
            raise ValueError("PORT must be between 0 and 65535")
        return config
