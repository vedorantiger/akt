# ui/dialogs/trash_dialog.py
"""Діалог корзини для відновлення видалених клієнтів"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QFont
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition, PrimaryPushButton
import os
import json
import shutil
from datetime import datetime


class TrashDialog(QDialog):
    """Діалог корзини для управління видаленими елементами"""
    
    # Сигнал для сповіщення про відновлення клієнта
    client_restored = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗑️ Корзина")
        self.setModal(True)
        self.resize(900, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #F9FAFB;
            }
        """)
        
        self._init_ui()
        self._load_trash_items()
    
    def _init_ui(self):
        """Створює інтерфейс діалогу"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок та кнопка очищення
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🗑️ КОРЗИНА")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #374151;")
        
        clear_button = QPushButton("🧹 Очистити корзину")
        clear_button.setFixedHeight(40)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
        """)
        clear_button.clicked.connect(self._clear_all_trash)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        
        # Таблиця елементів
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Тип", "Назва", "Власник", "Дата видалення", "Дії"
        ])
        
        # Налаштування таблиці
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowHeight(0, 60)  # Фіксована висота рядків 60px
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
                selection-background-color: #DBEAFE;
                selection-color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #374151;
                font-weight: 600;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
        """)
        
        # Розтягуємо стовпці
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Тип
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Назва
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Власник
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Дата
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Дії
        
        # Кнопка закриття
        close_button = QPushButton("Закрити")
        close_button.setFixedHeight(40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_button.clicked.connect(self.accept)
        
        # Додаємо до макету
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.table)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)
    
    def _load_trash_items(self):
        """Завантажує елементи з корзини"""
        trash_dir = "data/trash"
        if not os.path.exists(trash_dir):
            return
        
        items = []
        
        # Перевіряємо папки клієнтів в корзині
        for item_name in os.listdir(trash_dir):
            item_path = os.path.join(trash_dir, item_name)
            if os.path.isdir(item_path):
                # Це папка клієнта
                try:
                    # Шукаємо JSON файл клієнта
                    json_files = [f for f in os.listdir(item_path) if f.endswith('.json')]
                    if json_files:
                        json_path = os.path.join(item_path, json_files[0])
                        with open(json_path, 'r', encoding='utf-8') as f:
                            client_data = json.load(f)
                        
                        # Отримуємо дату видалення з мітки часу папки
                        stat = os.stat(item_path)
                        delete_date = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y")
                        
                        items.append({
                            'type': '👤 Клієнт',
                            'name': client_data.get('full_name', item_name),
                            'owner': '-',
                            'delete_date': delete_date,
                            'path': item_path,
                            'data': client_data
                        })
                except:
                    continue
        
        # Заповнюємо таблицю
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            # Встановлюємо висоту рядка
            self.table.setRowHeight(row, 60)
            
            # Тип
            self.table.setItem(row, 0, QTableWidgetItem(item['type']))
            
            # Назва
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            
            # Власник
            self.table.setItem(row, 2, QTableWidgetItem(item['owner']))
            
            # Дата видалення
            self.table.setItem(row, 3, QTableWidgetItem(item['delete_date']))
            
            # Кнопки дій
            self._add_action_buttons(row, item)
    
    def _add_action_buttons(self, row: int, item: dict):
        """Додає кнопки дій для рядка"""
        from PySide6.QtWidgets import QWidget, QHBoxLayout
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Кнопка відновлення
        restore_btn = QPushButton("♻️ Відновити")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0FDF4;
                color: #15803D;
                border: 1px solid #22C55E;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #DCFCE7;
                border-color: #16A34A;
            }
        """)
        restore_btn.clicked.connect(lambda: self._restore_item(item))
        
        # Кнопка видалення
        delete_btn = QPushButton("❌ Видалити")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #EF4444;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-color: #DC2626;
            }
        """)
        delete_btn.clicked.connect(lambda: self._permanent_delete_item(item))
        
        layout.addWidget(restore_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        
        self.table.setCellWidget(row, 4, widget)
    
    def _restore_item(self, item: dict):
        """Відновлює елемент з корзини"""
        result = MessageBox(
            title="♻️ Підтвердження відновлення",
            content=f"Відновити '{item['name']}'?",
            parent=self
        ).exec()
        
        if result == 1:  # 1 означає "Так" в QFluentWidgets
            try:
                # Відновлюємо клієнта
                if item['type'] == '👤 Клієнт':
                    clients_dir = "data/clients"
                    os.makedirs(clients_dir, exist_ok=True)
                    
                    # Переміщуємо JSON файл назад
                    json_files = [f for f in os.listdir(item['path']) if f.endswith('.json')]
                    if json_files:
                        src_path = os.path.join(item['path'], json_files[0])
                        dst_path = os.path.join(clients_dir, json_files[0])
                        shutil.move(src_path, dst_path)
                    
                    # Видаляємо папку з корзини
                    shutil.rmtree(item['path'])
                
                InfoBar.success(
                    title="Успіх",
                    content=f"'{item['name']}' відновлено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                # Оновлюємо таблицю
                self._load_trash_items()
                
                # Сповіщаємо головне вікно про відновлення
                self.client_restored.emit()
                
            except Exception as e:
                InfoBar.error(
                    title="Помилка",
                    content=f"Помилка відновлення: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def _permanent_delete_item(self, item: dict):
        """Безповоротно видаляє елемент"""
        result = MessageBox(
            title="❌ Попередження",
            content=f"БЕЗПОВОРОТНО видалити '{item['name']}'?\n\nЦю дію НЕ МОЖНА буде скасувати!",
            parent=self
        ).exec()
        
        if result == 1:  # 1 означає "Так" в QFluentWidgets
            try:
                shutil.rmtree(item['path'])
                
                InfoBar.success(
                    title="Успіх",
                    content=f"'{item['name']}' безповоротно видалено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                # Оновлюємо таблицю
                self._load_trash_items()
                
            except Exception as e:
                InfoBar.error(
                    title="Помилка",
                    content=f"Помилка видалення: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def _clear_all_trash(self):
        """Очищає всю корзину"""
        result = MessageBox(
            title="🧹 Попередження",
            content="БЕЗПОВОРОТНО видалити ВСІ елементи з корзини?\n\nЦю дію НЕ МОЖНА буде скасувати!",
            parent=self
        ).exec()
        
        if result == 1:  # 1 означає "Так" в QFluentWidgets
            try:
                trash_dir = "data/trash"
                if os.path.exists(trash_dir):
                    shutil.rmtree(trash_dir)
                    os.makedirs(trash_dir, exist_ok=True)
                
                InfoBar.success(
                    title="Успіх",
                    content="Корзину очищено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                # Оновлюємо таблицю
                self._load_trash_items()
                
            except Exception as e:
                InfoBar.error(
                    title="Помилка",
                    content=f"Помилка очищення: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
