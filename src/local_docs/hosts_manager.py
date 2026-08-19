"""Management of the marked local-docs block in the hosts file."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from pathlib import Path

START_MARKER = "# === AIOHTTP LOCAL SERVERS START ==="
END_MARKER = "# === AIOHTTP LOCAL SERVERS END ==="


class HostsManager:
    def __init__(self, path: Path) -> None:
        self.path = path

    @staticmethod
    def _without_block(lines: list[str]) -> list[str]:
        result: list[str] = []
        inside = False
        for line in lines:
            if START_MARKER in line:
                inside = True
                continue
            if END_MARKER in line:
                inside = False
                continue
            if not inside:
                result.append(line)
        return result

    def _write(self, lines: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        original_stat = self.path.stat() if self.path.exists() else None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as temporary:
                temporary.writelines(lines)
                temporary_path = Path(temporary.name)
            if original_stat is not None:
                os.chmod(temporary_path, original_stat.st_mode)
                if hasattr(os, "chown") and os.geteuid() == 0:
                    os.chown(temporary_path, original_stat.st_uid, original_stat.st_gid)
        except PermissionError as error:
            raise PermissionError(
                f"Cannot modify hosts file {self.path}; "
                "run local-docs with administrator privileges"
            ) from error
        try:
            os.replace(temporary_path, self.path)
        finally:
            temporary_path.unlink(missing_ok=True)

    def update(self, domains: Iterable[str]) -> None:
        lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        block = [f"\n{START_MARKER}\n"]
        block.extend(f"127.0.0.1  {domain}\n" for domain in sorted(set(domains)))
        block.append(f"{END_MARKER}\n")
        self._write(self._without_block(lines) + block)

    def clean(self) -> None:
        if not self.path.exists():
            return
        lines = self._without_block(self.path.read_text(encoding="utf-8").splitlines(keepends=True))
        self._write(lines)
