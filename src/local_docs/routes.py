"""HTTP handlers for the local documentation server."""

from aiohttp import web

from local_docs.index_renderer import IndexRenderer
from local_docs.site_registry import SiteRegistry
from local_docs.static_files import resolve_static_path


async def handle_docs_local(request: web.Request) -> web.Response:
    renderer: IndexRenderer = request.app["index_renderer"]
    port: int = request.app["port"]
    registry: SiteRegistry = request.app["site_registry"]
    return web.Response(text=renderer.render(registry.names, port), content_type="text/html")


async def handle_static_file(request: web.Request) -> web.StreamResponse:
    registry: SiteRegistry = request.app["site_registry"]
    site_path = registry.get(request.host)
    if site_path is None:
        raise web.HTTPNotFound(text="Сайт не найден")
    target, error_status = resolve_static_path(site_path, request.match_info.get("tail", ""))
    if error_status == 403:
        raise web.HTTPForbidden(text="Доступ запрещен")
    if target is None:
        raise web.HTTPNotFound(text="Страница не найдена")
    return web.FileResponse(target)
