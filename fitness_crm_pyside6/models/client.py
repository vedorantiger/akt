# models/client.py
"""Модель клієнта"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, SQLModel
import uuid


class ClientBase(SQLModel):
    """Базова модель клієнта для SQLModel"""
    # Основні дані
    first_name: str = SQLField(max_length=100)
    last_name: str = SQLField(max_length=100)
    middle_name: Optional[str] = SQLField(default=None, max_length=100)
    phone: str = SQLField(max_length=20, unique=True)
    email: Optional[str] = SQLField(default=None, max_length=100)
    birth_date: Optional[datetime] = None
    
    # Додаткова інформація
    notes: Optional[str] = None
    is_active: bool = SQLField(default=True)
    
    # Дати
    created_at: datetime = SQLField(default_factory=datetime.now)
    updated_at: datetime = SQLField(default_factory=datetime.now)
    last_visit: Optional[datetime] = None


class Client(ClientBase, table=True):
    """Модель клієнта для бази даних"""
    __tablename__ = "clients"
    
    id: str = SQLField(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    @property
    def full_name(self) -> str:
        """Повне ім'я клієнта"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    @property
    def folder_name(self) -> str:
        """Назва папки для збереження файлів клієнта"""
        return f"{self.last_name}_{self.first_name}_{self.id}"
    
    def get_age(self) -> Optional[int]:
        """Розраховує вік клієнта"""
        if not self.birth_date:
            return None
        today = datetime.now().date()
        birth = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date
        age = today.year - birth.year
        if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
            age -= 1
        return age
    
    def get_client_directory(self):
        """Отримати директорію клієнта"""
        from pathlib import Path
        
        # Простий шлях до папки клієнта
        base_dir = Path(__file__).parent.parent
        clients_dir = base_dir / "data" / "clients"
        clients_dir.mkdir(parents=True, exist_ok=True)
        
        client_dir = clients_dir / f"client_{self.id}"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # Створюємо підпапки
        subdirs = ["photos", "documents", "testing", "reports", "other"]
        for subdir in subdirs:
            (client_dir / subdir).mkdir(exist_ok=True)
            
        return client_dir
    
    def create_client_structure(self):
        """Створити структуру папок для клієнта"""
        try:
            client_dir = self.get_client_directory()
            print(f"✅ Створено структуру папок для клієнта {self.full_name}")
            return client_dir
        except Exception as e:
            print(f"❌ Помилка при створенні структури для клієнта {self.id}: {e}")
            raise
    
    def log_activity(self, activity: str):
        """Логувати активність клієнта"""
        print(f"👤 Клієнт {self.full_name} ({self.id}): {activity}")
    
    def update_last_visit(self):
        """Оновити дату останнього візиту"""
        self.last_visit = datetime.now()
        self.updated_at = datetime.now()
        self.log_activity("Оновлено дату останнього візиту")


class ClientCreate(BaseModel):
    """Схема для створення клієнта"""
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = None
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    """Схема для оновлення клієнта"""
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None