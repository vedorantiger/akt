# config/database.py
"""Налаштування бази даних"""
import os
from pathlib import Path
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event
from rich.console import Console

# Rich консоль для красивого виводу
console = Console()

# Простий шлях до бази даних
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'fitness_crm.db'}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Встановіть True для дебагу SQL
)


# Налаштування для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Налаштування SQLite для кращої продуктивності"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
    console.print("[bold blue]🔧 Налаштовано SQLite PRAGMA[/bold blue]")


def init_db():
    """Ініціалізація бази даних"""
    try:
        # Імпортуємо всі моделі
        from models.client import Client  # noqa: F401
        
        # Створюємо всі таблиці
        SQLModel.metadata.create_all(engine)
        console.print("[bold green]✅ База даних ініціалізована успішно![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Помилка ініціалізації бази даних: {e}[/bold red]")
        raise


def get_session() -> Session:
    """Отримати сесію для роботи з БД"""
    try:
        session = Session(engine)
        return session
    except Exception as e:
        console.print(f"[bold red]❌ Помилка створення сесії: {e}[/bold red]")
        raise


def test_connection():
    """Тестувати з'єднання з базою даних"""
    try:
        with get_session() as session:
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            console.print("[bold green]✅ З'єднання з базою даних успішне[/bold green]")
            return True
    except Exception as e:
        console.print(f"[bold red]❌ Помилка з'єднання з базою даних: {e}[/bold red]")
        return False


# Ініціалізуємо БД при імпорті
db_file = DATABASE_DIR / "fitness_crm.db"
if not db_file.exists():
    console.print("[bold cyan]🆕 Створюємо нову базу даних[/bold cyan]")
    init_db()
else:
    console.print("[bold cyan]📂 Використовуємо існуючу базу даних[/bold cyan]")
    # Перевіряємо з'єднання
    test_connection()