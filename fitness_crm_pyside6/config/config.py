"""Проста конфігурація для Fitness CRM"""

from pathlib import Path

# Базова інформація
APP_NAME = "Fitness CRM"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Denis"

# Шляхи
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

# Створюємо директорії
DATABASE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Налаштування вікна
WINDOW_SIZE = (1200, 800)
WINDOW_TITLE = f"{APP_NAME} - Система управління клієнтами"

print(f"📁 Конфігурація завантажена: {APP_NAME} v{APP_VERSION}")