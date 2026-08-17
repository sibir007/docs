import asyncio
import logging
import os
import socket
from pathlib import Path

from aiohttp import web

import change_hosts

# Импортируем наши новые функции управления документацией
from docs import get_running_docs, init_docs, open_browser_delayed
from lib import get_sites_names

LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = (
    getattr(logging, LOG_LEVEL_STR) if hasattr(logging, LOG_LEVEL_STR) else logging.WARNING
)
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.resolve()
SITES_DIR = BASE_DIR / "sites"
SERVER_PORT = int(os.getenv("PORT", "8080"))  # Выносим порт в переменную


async def handle_docs_local(request: web.Request) -> web.Response:
    """Эндпоинт, который отдает сгенерированную таблицу."""
    RUNNING_DOCS = get_running_docs()
    if RUNNING_DOCS is None:
        return web.Response(
            text="Документация не инициализирована или уже очищена.", status=503
        )

    return web.Response(text=RUNNING_DOCS, content_type="text/html", charset="utf-8")


async def handle_static_file(request: web.Request) -> web.Response:
    """Ваш существующий (исправленный) хендлер для статики сайтов."""
    host = request.url.host
    if not host:
        return web.Response(text="Не удалось определить хост.", status=400)

    site_path = (SITES_DIR / host).resolve()
    is_dir = await asyncio.to_thread(site_path.is_dir)
    if not is_dir:
        return web.Response(text=f"Сайт '{host}' не найден.", status=404)

    tail = request.match_info.get("tail", "").lstrip("/")
    target_path = (site_path / tail).resolve()

    if site_path not in target_path.parents and target_path != site_path:
        return web.Response(text="Доступ запрещен", status=403)

    async def check_file(path: Path) -> bool:
        return await asyncio.to_thread(path.is_file)

    async def check_dir(path: Path) -> bool:
        return await asyncio.to_thread(path.is_dir)

    if await check_dir(target_path):
        index_file = target_path / "index.html"
        if await check_file(index_file):
            return web.FileResponse(index_file)
        return web.Response(text="Индексный файл не найден", status=404)

    if await check_file(target_path):
        return web.FileResponse(target_path)

    html_fallback = target_path.with_suffix(target_path.suffix + ".html")
    if site_path in html_fallback.parents or html_fallback == site_path:  # noqa: SIM102
        if await check_file(html_fallback):
            return web.FileResponse(html_fallback)

    return web.Response(text="Страница не найдена", status=404)


async def start_browser_callback(app: web.Application) -> None:
    """Системный колбэк aiohttp, который срабатывает сразу после старта сервера."""
    docs_url = f"http://127.0.0.1:{SERVER_PORT}/docs_local"
    logger.info(f"Запуск браузера со страницей: {docs_url}")
    # Запускаем фоновую задачу, чтобы не блокировать старт самого приложения
    asyncio.create_task(open_browser_delayed(docs_url, delay=0.5))



logger = logging.getLogger(__name__)

async def find_free_port(preferred_port: int = 0) -> int:
    """
    Проверяет, свободен ли preferred_port. Если занят или равен 0,
    возвращает случайный свободный порт, выделенный системой.
    Выполняется в отдельном потоке, чтобы не блокировать event loop.
    """
    def _check_and_find():
        # 1. Проверяем предпочтительный порт, если он указан
        if preferred_port > 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    # Пытаемся занять порт на локальном интерфейсе
                    s.bind(("127.0.0.1", preferred_port))
                    return preferred_port
                except OSError:
                    logger.warning(f"Порт {preferred_port} уже занят. Ищем альтернативный...")

        # 2. Если занят или не указан, просим ОС выдать любой свободный
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Передача '0' заставляет ОС автоматически выбрать свободный порт
            s.bind(("127.0.0.1", 0))
            # Узнаем, какой именно порт выделила система
            free_port = s.getsockname()[1]
            return free_port

    # Запускаем синхронные операции с сокетами в потоке (чтобы Ruff не ругался)
    return await asyncio.to_thread(_check_and_find)



async def main_async():
    sites_names = get_sites_names()
    
    # 1. Обновляем хосты
    change_hosts.update_hosts_on_start(sites_names)
    
    # 2. Ищем свободный порт (пробуем взять 8080 из конфига/среды, либо любой свободный)
    default_port = int(os.getenv("PORT", "8080"))
    server_port = await find_free_port(preferred_port=default_port)
    logger.info(f"Используем свободный порт: {server_port}")
    
    # Передаем актуальный порт в глобальную переменную для колбэка браузера
    global SERVER_PORT
    SERVER_PORT = server_port

    # 3. Инициализируем HTML-документ в памяти с правильным портом
    init_docs(sites_names, port=server_port)

    app = web.Application()
    app.router.add_get('/docs_local', handle_docs_local)
    app.router.add_get('/{tail:.*}', handle_static_file)
    app.on_startup.append(start_browser_callback)
    
    # Настраиваем runner вручную, так как web.run_app() синхронный, 
    # а нам нужно находиться внутри работающего event loop
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', server_port)
    
    # Создаем событие, которое будет держать сервер запущенным
    stop_event = asyncio.Event()

    try:
        await site.start()
        # Вызываем триггер запуска браузера вручную, 
        # так как при ручном запуске TCPSite хук on_startup не срабатывает автоматически
        await start_browser_callback(app)
        
        logger.info(f"Сервер запущен на http://0.0.0.0:{server_port}")
        
        # Вместо цикла "while True" просто ждем, пока событие не активируется
        # Программа «застынет» на этой строке, продолжая асинхронно обрабатывать запросы
        await stop_event.wait()

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания (Ctrl+C)...")
    finally:
        logger.info("Выход из приложения. Очистка ресурсов...")
        
        # 1. Сначала плавно останавливаем прием новых сетевых запросов
        await site.stop() 
        
        # 2. Очищаем документацию и hosts

        change_hosts.clean_hosts_on_stop()
        
        # 3. Безопасно закрываем все открытые соединения пользователей
        await runner.cleanup()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

