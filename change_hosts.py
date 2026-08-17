import logging
import os
import sys
from collections.abc import Iterable

logger = logging.getLogger(__name__)

SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")

# Определяем путь к файлу hosts в зависимости от ОС
if sys.platform.startswith("win"):
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
else:
    HOSTS_PATH = "/etc/hosts"

# Метки для автоматического блока в файле hosts
START_MARKER = "# === AIOHTTP LOCAL SERVERS START ==="
END_MARKER = "# === AIOHTTP LOCAL SERVERS END ==="


def update_hosts_on_start(host_names: Iterable[str]) -> None:
    """Добавляет локальные домены в файл hosts."""

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Проверяем, не остались ли метки от прошлого аварийного завершения
        clean_lines = []
        skip = False
        for line in lines:
            if START_MARKER in line:
                skip = True
                continue

            if END_MARKER in line:
                skip = False
                continue
            if not skip:
                clean_lines.append(line)

        # Формируем блок новых записей
        new_lines = [f"\n{START_MARKER}\n"]
        for domain in host_names:
            logging.debug(f"127.0.0.1  {domain}")
            new_lines.append(f"127.0.0.1  {domain}\n")
        new_lines.append(f"{END_MARKER}\n")

        # Перезаписываем файл hosts
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(clean_lines + new_lines)

        print("[HOSTS] Доменные имена успешно добавлены в систему.")
    except PermissionError:
        print(
            f"[ERROR] Нет прав на запись в {HOSTS_PATH}."
            f"\nПожалуйста, запустите скрипт от имени Администратора (Windows) или через sudo (Linux/macOS)."
        )
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Не удалось обновить файл hosts: {e}")
        sys.exit(1)


def clean_hosts_on_stop():
    """Удаляет локальные домены из файла hosts."""
    print("\n[HOSTS] Очистка файла hosts...")
    if not os.path.exists(HOSTS_PATH):
        return

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        clean_lines = []
        skip = False
        for line in lines:
            if START_MARKER in line:
                skip = True
                continue
            if END_MARKER in line:
                skip = False
                continue
            if not skip:
                clean_lines.append(line)

        # Убираем лишние пустые строки в конце файла, если они образовались
        if clean_lines and clean_lines[-1].strip() == "":
            clean_lines.pop()

        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(clean_lines)

        print("[HOSTS] Доменные имена успешно удалены.")
    except Exception as e:
        print(f"[ERROR] Не удалось очистить файл hosts: {e}")
