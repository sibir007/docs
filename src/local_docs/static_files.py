"""Safe static file resolution for a discovered site."""

from __future__ import annotations

from pathlib import Path


def resolve_static_path(site_path: Path, tail: str) -> tuple[Path | None, int | None]:
    root = site_path.resolve()
    target = (root / tail.lstrip("/")).resolve()
    if target != root and root not in target.parents:
        return None, 403

    if target.is_dir():
        index = target / "index.html"
        return (index, None) if index.is_file() else (None, 404)
    if target.is_file():
        return target, None

    fallback = target.with_suffix(target.suffix + ".html")
    if (fallback == root or root in fallback.parents) and fallback.is_file():
        return fallback, None
    return None, 404
