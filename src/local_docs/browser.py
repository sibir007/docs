"""Optional delayed browser opening."""

from __future__ import annotations

import asyncio
import logging
import webbrowser

logger = logging.getLogger(__name__)


async def open_browser_delayed(url: str, delay: float = 0.5) -> None:
    await asyncio.sleep(delay)
    try:
        await asyncio.to_thread(webbrowser.open, url)
    except Exception:
        logger.warning("Could not open browser at %s", url, exc_info=True)
