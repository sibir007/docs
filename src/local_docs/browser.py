"""Optional delayed browser opening."""

from __future__ import annotations

import asyncio
import logging
import os
import pwd
import shlex
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


async def open_browser_delayed(url: str, delay: float = 0.5) -> None:
    await asyncio.sleep(delay)
    try:
        await asyncio.to_thread(_open_browser, url)
    except Exception:
        logger.warning("Could not open browser at %s", url, exc_info=True)


def _open_browser(url: str) -> None:
    sudo_user = os.environ.get("SUDO_USER")
    if not sudo_user:
        _open_with_browser(url)
        return

    # The server may need root for /etc/hosts, but the GUI belongs to the user
    # who invoked sudo. Run the desktop opener in that user's session.
    user_id = os.environ.get("SUDO_UID")
    user_home = Path(pwd.getpwnam(sudo_user).pw_dir)
    environment = {
        name: value
        for name in (
            "DBUS_SESSION_BUS_ADDRESS",
            "DISPLAY",
            "WAYLAND_DISPLAY",
            "XAUTHORITY",
        )
        if (value := os.environ.get(name)) is not None
    }
    xauthority = os.environ.get("XAUTHORITY")
    if not xauthority:
        user_xauthority = user_home / ".Xauthority"
        if user_xauthority.exists():
            xauthority = str(user_xauthority)
    if xauthority:
        environment["XAUTHORITY"] = xauthority
    if user_id:
        environment["XDG_RUNTIME_DIR"] = f"/run/user/{user_id}"
    browser = _find_browser()
    if browser is None:
        logger.warning("No supported graphical browser found; open %s manually", url)
        return
    subprocess.run(
        [
            "sudo",
            "-u",
            sudo_user,
            "-H",
            "env",
            *[f"{name}={value}" for name, value in environment.items()],
            browser,
            url,
        ],
        check=False,
    )


def _find_browser() -> str | None:
    configured = os.environ.get("BROWSER")
    candidates = [configured] if configured else []
    candidates.extend(
        (
            "firefox",
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
            "brave-browser",
        )
    )
    for candidate in candidates:
        if not candidate:
            continue
        executable = shutil.which(shlex.split(candidate)[0])
        if executable:
            return executable
    return None


def _open_with_browser(url: str) -> None:
    browser = _find_browser()
    if browser is None:
        logger.warning("No supported graphical browser found; open %s manually", url)
        return
    subprocess.Popen([browser, url])
