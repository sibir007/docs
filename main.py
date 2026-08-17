import asyncio
from pathlib import Path
import webbrowser

from aiohttp import web

# from aiohttp_index import IndexMiddleware
from aiohttp_index import IndexMiddleware  # type: ignore

SITES_DIR = "./sites"
START_PORT = 8031



# sites = ["python-3.12.0-docs-html", "site_FastAPI", "sqlalchemy_20"]
# ports = [8031, 8032, 8033]
# # app = web.Application(middlewares=[IndexMiddleware()]) # type: ignore
# # app.router.add_static('/', './site_FastAPI')
# # app.router.add_static('/', './python-3.12.0-docs-html')
# # async def index(request):
# #     # Redirect root to index.html
# #     request.
# #     return web.HTTPFound('/index.html')

def get_sites_names():
    p = Path(SITES_DIR)
    return [d.stem for d in p.iterdir() if d.is_dir() and not d.stem.startswith("_")]


# @web.middleware
# async def html_extension_middleware(request, handler):
#     path = request.path
    

#     new_path = f"{path}.html"
        
#     # Клонируем запрос с измененным путем
#     request = request.clone(rel_url=new_path)
    
#     return await handler(request)


async def serve_site(site_name: str, port: int):
    # async def serve_site(site_name: str, host: str, port: int):
    path_middleware = web.normalize_path_middleware(
    append_slash=True, 
    merge_slashes=True
)
    app = web.Application(middlewares=[IndexMiddleware(), path_middleware])  # type: ignore
    app.router.add_static("/", f"{SITES_DIR}/{site_name}") # type: ignore
    await web._run_app(app=app, port=port) # type: ignore



async def sites_serving(sites: list[str], ports: list[int]) -> None:
    # names = sites_names() if sites is None else sites
    # names_len = len(names)
    # ports = range(START_PORT, START_PORT + names_len)
    servs = [serve_site(site, port) for site, port in zip(sites, ports)]

    await asyncio.gather(*servs)


def open_browser_pages(ports: list[int])-> None:

    webbrowser.open_new(f"http://localhost:{ports[0]}")
    
    for port in ports[1:]:
        url = f"http://localhost:{port}"
        print(f"Opening {url} in browser...")
        webbrowser.open(url)


async def main():
    loop = asyncio.get_running_loop()
    sites = await loop.run_in_executor(None, get_sites_names)
    ports = [p for p in range(START_PORT, START_PORT + len(sites))]
    serving_task =  sites_serving(sites, ports)
    browsing_task = loop.run_in_executor(None, open_browser_pages, ports)
    await asyncio.gather(*[serving_task, browsing_task])

# app = web.Application()

# app.add_routes([web.static('/', './sqlalchemy_20', show_index=True)])
# # 1. Add redirect for the root URL
# app.router.add_get('/', index)

# # 2. Serve the static directory
# # append_version=True adds hashes for cache busting
# app.router.add_static('/', path='./site_FastAPI', name='fastapi', show_index=True)

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(sites_serving())
    # asyncio.run(supervisor())
    # web.run_app(app, port=8080)

# if __name__ == "__main__":
#     main()
