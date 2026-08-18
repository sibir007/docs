"""Discovery and safe host-to-site mapping."""

from __future__ import annotations

from pathlib import Path


class SiteRegistry:
    def __init__(self, sites_dir: Path) -> None:
        self.sites_dir = sites_dir.resolve()
        self._sites: dict[str, Path] = {}

    def discover(self) -> list[str]:
        if not self.sites_dir.is_dir():
            self._sites = {}
            return []
        sites: dict[str, Path] = {}
        for path in self.sites_dir.iterdir():
            resolved = path.resolve()
            if path.name.startswith((".", "_")) or not path.is_dir():
                continue
            if self.sites_dir not in resolved.parents:
                continue
            sites[path.name] = resolved
        self._sites = dict(sorted(sites.items()))
        return list(self._sites)

    @property
    def names(self) -> list[str]:
        return list(self._sites)

    def get(self, host: str) -> Path | None:
        return self._sites.get(host.split(":", 1)[0].lower())
