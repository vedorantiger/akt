# models/client_list.py
"""Клас для керування списком клієнтів"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, or_
from models.client import Client, ClientCreate, ClientUpdate
from config.database import engine
import json
import os


class ClientList:
    """Керування списком клієнтів"""
    
    def __init__(self):
        self.session = Session(engine)
    
    def get_all(self, active_only: bool = True) -> List[Client]:
        """Отримати всіх клієнтів"""
        statement = select(Client)
        if active_only:
            statement = statement.where(Client.is_active == True)
        
        statement = statement.order_by(Client.last_name, Client.first_name)
        return self.session.exec(statement).all()
    
    def search(self, query: str) -> List[Client]:
        """Пошук клієнтів за іменем або телефоном"""
        if not query:
            return self.get_all()
        
        statement = select(Client).where(
            or_(
                Client.first_name.contains(query),
                Client.last_name.contains(query),
                Client.phone.contains(query),
                Client.email.contains(query)
            )
        ).where(Client.is_active == True)
        
        return self.session.exec(statement).all()
    
    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Отримати клієнта за ID"""
        return self.session.get(Client, client_id)
    
    def create(self, client_data: ClientCreate) -> Client:
        """Створити нового клієнта"""
        client = Client(**client_data.dict())
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        
        # Створюємо папку для клієнта
        self._create_client_folder(client)
        
        return client
    
    def update(self, client_id: str, client_data: ClientUpdate) -> Optional[Client]:
        """Оновити дані клієнта"""
        client = self.get_by_id(client_id)
        if not client:
            return None
        
        update_data = client_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)
        
        client.updated_at = datetime.now()
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        
        return client
    
    def delete(self, client_id: str, soft_delete: bool = True) -> bool:
        """Видалити клієнта (м'яке видалення за замовчуванням)"""
        client = self.get_by_id(client_id)
        if not client:
            return False
        
        if soft_delete:
            client.is_active = False
            client.updated_at = datetime.now()
            self.session.add(client)
        else:
            self.session.delete(client)
        
        self.session.commit()
        return True
    
    def get_recent(self, limit: int = 10) -> List[Client]:
        """Отримати останніх відвіданих клієнтів"""
        statement = select(Client).where(
            Client.is_active == True,
            Client.last_visit.is_not(None)
        ).order_by(Client.last_visit.desc()).limit(limit)
        
        return self.session.exec(statement).all()
    
    def update_last_visit(self, client_id: str) -> Optional[Client]:
        """Оновити дату останнього візиту"""
        client = self.get_by_id(client_id)
        if client:
            client.last_visit = datetime.now()
            client.updated_at = datetime.now()
            self.session.add(client)
            self.session.commit()
            self.session.refresh(client)
        return client
    
    def _create_client_folder(self, client: Client):
        """Створює структуру папок для клієнта"""
        base_path = os.path.join("data", "clients", client.folder_name)
        folders = ["photos", "documents", "testing", "other", "reports"]
        
        # Створюємо основну папку
        os.makedirs(base_path, exist_ok=True)
        
        # Створюємо підпапки
        for folder in folders:
            os.makedirs(os.path.join(base_path, folder), exist_ok=True)
        
        # Створюємо файл даних клієнта
        client_data_path = os.path.join(base_path, "client_data.json")
        if not os.path.exists(client_data_path):
            with open(client_data_path, 'w', encoding='utf-8') as f:
                json.dump(client.dict(), f, ensure_ascii=False, indent=2, default=str)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Отримати статистику по клієнтах"""
        total = self.session.exec(
            select(Client).where(Client.is_active == True)
        ).all()
        
        recent_month = self.session.exec(
            select(Client).where(
                Client.is_active == True,
                Client.created_at >= datetime.now().replace(day=1)
            )
        ).all()
        
        return {
            "total_active": len(total),
            "new_this_month": len(recent_month),
            "total_visits_today": 0,  # Буде реалізовано пізніше
            "scheduled_today": 0      # Буде реалізовано пізніше
        }
    
    def __del__(self):
        """Закриваємо сесію при знищенні об'єкта"""
        if hasattr(self, 'session'):
            self.session.close()