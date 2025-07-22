# config/logger.py
"""Система логування для Fitness CRM"""

import os
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from typing import Optional

# Ініціалізуємо Rich Console
rich_console = Console()


class FitnessLogger:
    """Кастомна система логування для Fitness CRM"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self._setup_logger()
    
    def _setup_logger(self):
        """Налаштування логгера"""
        # Видаляємо стандартний обробник
        logger.remove()
        
        # Консольний вивід з кольорами
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # Основний лог файл
        current_month = datetime.now().strftime("%Y_%m")
        logger.add(
            self.logs_dir / f"app_{current_month}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 month",
            retention="6 months",
            compression="zip",
            encoding="utf-8"
        )
        
        # Лог помилок
        logger.add(
            self.logs_dir / f"errors_{current_month}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="1 month", 
            retention="12 months",
            compression="zip",
            encoding="utf-8"
        )
        
        # Лог UI подій
        logger.add(
            self.logs_dir / f"ui_{current_month}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            rotation="1 month",
            retention="3 months",
            compression="zip",
            encoding="utf-8",
            filter=lambda record: "UI" in record["extra"].get("category", "")
        )
        
        # Лог бази даних
        logger.add(
            self.logs_dir / f"database_{current_month}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 month",
            retention="6 months", 
            compression="zip",
            encoding="utf-8",
            filter=lambda record: "DB" in record["extra"].get("category", "")
        )

    def get_logger(self, name: str, category: Optional[str] = None):
        """Отримати логгер з вказаним ім'ям та категорією"""
        bound_logger = logger.bind(category=category or "APP")
        return bound_logger
    
    def log_startup(self):
        """Лог запуску програми"""
        logger.info("🚀 Fitness CRM запущено")
        logger.info(f"📁 Робоча директорія: {os.getcwd()}")
        logger.info(f"🐍 Python версія: {sys.version}")
    
    def log_shutdown(self):
        """Лог завершення програми"""
        logger.info("🛑 Fitness CRM завершено")


# Глобальний екземпляр логгера
fitness_logger = FitnessLogger()

# Зручні функції для різних категорій
def get_app_logger():
    """Логгер для основної програми"""
    return fitness_logger.get_logger("APP", "APP")

def get_ui_logger():
    """Логгер для UI подій"""
    return fitness_logger.get_logger("UI", "UI")

def get_db_logger():
    """Логгер для бази даних"""
    return fitness_logger.get_logger("DB", "DB")

def get_api_logger():
    """Логгер для API запитів"""
    return fitness_logger.get_logger("API", "API")


# Rich utilities для красивого консольного виводу
def print_success(message: str):
    """Красивий вивід успішного повідомлення"""
    rich_console.print(f"[bold green]✅ {message}[/bold green]")

def print_error(message: str):
    """Красивий вивід помилки"""
    rich_console.print(f"[bold red]❌ {message}[/bold red]")

def print_warning(message: str):
    """Красивий вивід попередження"""
    rich_console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")

def print_info(message: str):
    """Красивий вивід інформації"""
    rich_console.print(f"[bold blue]ℹ️ {message}[/bold blue]")


# Ініціалізуємо при імпорті
if __name__ != "__main__":
    fitness_logger.log_startup()
