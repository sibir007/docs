import asyncio
import os
import re
import webbrowser
from pathlib import Path

# В этой переменной будет жить сгенерированный HTML в памяти
RUNNING_DOCS: str | None = None

TEMPLATE_PATH = Path(__file__).parent / "template.html"

def get_running_docs() -> str | None:
    return RUNNING_DOCS

def init_docs(sites_names: list[str], port: int) -> None:
    """Генерирует HTML на основе шаблона и списка сайтов, сохраняя в память."""
    global RUNNING_DOCS

    if not TEMPLATE_PATH.exists():
        # Фоллбек на случай, если файла шаблона нет рядом
        RUNNING_DOCS = "<h1>Ошибка: template.html не найден</h1>"
        return

    template_content = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Формируем строки таблицы
    rows = []
    for site in sites_names:
        # Формируем ссылку вида http://domain.local:8080
        # Если порт стандартный (80), его можно не указывать
        url = f"http://{site}" if port == 80 else f"http://{site}:{port}"

        row = f"""
        <tr>
            <td><strong>{site}</strong></td>
            <td><span class="status-badge">Активен</span></td>
            <td><a href="{url}" target="_blank" class="site-link">Открыть сайт</a></td>
        </tr>
        """
        rows.append(row)

    # Объединяем строки и вставляем в плейсхолдер шаблона
    table_rows_html = "\n".join(rows)
    RUNNING_DOCS = template_content.replace(
        "<!-- SITES_ROWS_PLACEHOLDER -->", table_rows_html
    )


def clear_docs() -> None:
    """Очищает сгенерированный документ из памяти при выходе."""
    global RUNNING_DOCS
    RUNNING_DOCS = None


async def open_browser_delayed(url: str, delay: float = 0.5) -> None:
    """Запускает браузер от имени реального пользователя без блокирования event loop."""
    await asyncio.sleep(delay)
    
    # Получаем имя пользователя, который запустил команду через sudo
    real_user = os.getenv("SUDO_USER")
    
    if real_user and real_user != "root":
        try:
            # АСИНХРОННО получаем UID пользователя (исправляет Ruff ASYNC221)
            proc_id = await asyncio.create_subprocess_exec(
                "id", "-u", real_user,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            stdout, _ = await proc_id.communicate()
            
            if proc_id.returncode == 0:
                uid_str = stdout.decode().strip()
                
                # Подготавливаем переменные окружения для графики
                env = os.environ.copy()
                env["DISPLAY"] = os.getenv("DISPLAY", ":0")
                env["XDG_RUNTIME_DIR"] = f"/run/user/{uid_str}"
                
                # АСИНХРОННО запускаем браузер (исправляет Ruff ASYNC221)
                await asyncio.create_subprocess_exec(
                    "sudo", "-u", real_user, "xdg-open", url,
                    env=env,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                return
        except Exception:  # noqa: BLE001, S110
            pass  # Если асинхронный запуск через sudo не удался, идем в фоллбек

    # Фоллбек для обычного запуска (если запуск был не через sudo)
    await asyncio.to_thread(webbrowser.open, url)
