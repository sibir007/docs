"""Aiohttp application factory and server lifecycle."""

from __future__ import annotations

import asyncio
import logging

from aiohttp import web

from local_docs.browser import open_browser_delayed
from local_docs.config import AppConfig
from local_docs.hosts_manager import HostsManager
from local_docs.index_renderer import IndexRenderer
from local_docs.routes import handle_docs_local, handle_static_file
from local_docs.site_registry import SiteRegistry

logger = logging.getLogger(__name__)


def create_app(config: AppConfig, registry: SiteRegistry, port: int) -> web.Application:
    app = web.Application()
    app["site_registry"] = registry
    app["index_renderer"] = IndexRenderer()
    app["port"] = port
    app.router.add_get("/docs_local", handle_docs_local)
    app.router.add_get("/{tail:.*}", handle_static_file)
    return app


async def run_server(config: AppConfig) -> None:
    registry = SiteRegistry(config.sites_dir)
    site_names = registry.discover()
    hosts = HostsManager(config.hosts_path)
    runner: web.AppRunner | None = None
    browser_task: asyncio.Task[None] | None = None
    try:
        hosts.update(site_names)
        app = create_app(config, registry, config.preferred_port)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, config.bind_host, config.preferred_port)
        try:
            await site.start()
        except OSError:
            if config.preferred_port == 0:
                raise
            logger.warning(
                "Port %s is busy; selecting a free port", config.preferred_port
            )
            site = web.TCPSite(runner, config.bind_host, 0)
            await site.start()
        sockets = site._server.sockets if site._server is not None else []
        if not sockets:
            raise RuntimeError("Server started without a listening socket")
        actual_port = sockets[0].getsockname()[1]
        app["port"] = actual_port
        logger.info("Serving local documentation at http://%s:%s/docs_local", config.bind_host, actual_port)
        if config.open_browser:
            browser_task = asyncio.create_task(
                open_browser_delayed(f"http://{config.bind_host}:{actual_port}/docs_local")
            )
        await asyncio.Event().wait()
    finally:
        if browser_task is not None:
            browser_task.cancel()
            await asyncio.gather(browser_task, return_exceptions=True)
        if runner is not None:
            await runner.cleanup()
        hosts.clean()
