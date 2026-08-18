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
    def from_environment(cls, **overrides: object) -> AppConfig:
        base_dir = Path(__file__).resolve().parents[2]
        sites_dir = Path(os.getenv("SITES_DIR", str(base_dir / "sites")))
        port = int(os.getenv("PORT", "8080"))
        values = {
            "base_dir": base_dir,
            "sites_dir": sites_dir.expanduser().resolve(),
            "bind_host": os.getenv("HOST", "127.0.0.1"),
            "preferred_port": port,
            "open_browser": _env_bool("OPEN_BROWSER", True),
            "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
            "hosts_path": default_hosts_path(),
        }
        values.update({key: value for key, value in overrides.items() if value is not None})
        if not 0 <= int(values["preferred_port"]) <= 65535:
            raise ValueError("PORT must be between 0 and 65535")
        return cls(**values)
