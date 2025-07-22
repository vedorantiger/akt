# ui/widgets/list_item.py
"""Віджет елемента списку клієнтів"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont
from qfluentwidgets import CardWidget, ImageLabel, BodyLabel, StrongBodyLabel, TransparentToolButton
from qfluentwidgets import FluentIcon as FIF
import os
import webbrowser


class ListItemWidget(CardWidget):
    """Віджет елемента списку клієнта (компактний вигляд)"""
    
    clicked = Signal(str)  # Сигнал при кліку (передає ID клієнта)
    edit_requested = Signal(str)  # Сигнал для редагування
    delete_requested = Signal(str)  # Сигнал для видалення
    
    def __init__(self, client_data: dict, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        self.client_id = client_data.get('id', 'NO_ID')
        
        # Налаштування віджета
        self.setFixedHeight(140)  # Ще більша висота для кнопок 120x120
        self.setCursor(Qt.PointingHandCursor)
        self.setBorderRadius(8)
        
        self._init_ui()
        
    def _init_ui(self):
        """Створює інтерфейс елемента списку"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)
        
        # ===== АВАТАР (60x60) =====
        self.avatar = QLabel()
        self.avatar.setFixedSize(60, 60)
        self.avatar.setStyleSheet("""
            QLabel {
                background-color: #f1f3f4;
                border: 2px solid #e5e7eb;
                border-radius: 30px;
            }
        """)
        self.avatar.setAlignment(Qt.AlignCenter)
        
        # Завантажуємо аватар або встановлюємо заглушку
        self._load_avatar()
        
        main_layout.addWidget(self.avatar)
        
        # ===== ІНФОРМАЦІЯ ПРО КЛІЄНТА =====
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        # Ім'я
        self.name_label = StrongBodyLabel(self.client_data.get('full_name', 'Невідомий клієнт'))
        self.name_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #111827;")
        info_layout.addWidget(self.name_label)
        
        # Контактна інформація
        contact_info = []
        if self.client_data.get('phone'):
            contact_info.append(f"📞 {self.client_data['phone']}")
        if self.client_data.get('email'):
            contact_info.append(f"📧 {self.client_data['email']}")
        
        contact_text = " • ".join(contact_info) if contact_info else "Контактна інформація відсутня"
        self.contact_label = BodyLabel(contact_text)
        self.contact_label.setStyleSheet("color: #6b7280; font-size: 13px;")
        info_layout.addWidget(self.contact_label)
        
        # Додаткова інформація (вік, стать)
        additional_info = []
        
        # Обчислюємо вік з дати народження
        birth_date = self.client_data.get('birth_date')
        if birth_date and birth_date != "1900-01-01":
            try:
                from datetime import datetime
                birth_year = int(birth_date.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
                if age > 5 and age < 120:  # Валідний вік
                    additional_info.append(f"🎂 {age} років")
            except:
                pass
        
        if self.client_data.get('gender') and self.client_data['gender'] != "Оберіть стать":
            gender_icon = "👨" if self.client_data['gender'] == "Чоловік" else "👩"
            additional_info.append(f"{gender_icon} {self.client_data['gender']}")
        
        additional_text = " • ".join(additional_info) if additional_info else ""
        if additional_text:
            self.additional_label = BodyLabel(additional_text)
            self.additional_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
            info_layout.addWidget(self.additional_label)
        
        main_layout.addLayout(info_layout)
        main_layout.addStretch()  # Розтягуємо простір
        
        # ===== КНОПКИ ДІЙ =====
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        # Кнопка перегляду
        self.view_btn = TransparentToolButton(FIF.VIEW)
        self.view_btn.setFixedSize(120, 120)
        self.view_btn.setToolTip("Переглянути клієнта")
        self.view_btn.clicked.connect(lambda: self._show_development_message("ВЕДЕННЯ"))
        actions_layout.addWidget(self.view_btn)
        
        # Кнопка повідомлень
        self.message_btn = TransparentToolButton(FIF.MESSAGE)
        self.message_btn.setFixedSize(120, 120)
        self.message_btn.setToolTip("Повідомлення")
        self.message_btn.clicked.connect(lambda: self._show_development_message("ПОВІДОМЛЕННЯ"))
        actions_layout.addWidget(self.message_btn)
        
        # Кнопка AI помічника
        self.ai_btn = TransparentToolButton(FIF.ROBOT)
        self.ai_btn.setFixedSize(120, 120)
        self.ai_btn.setToolTip("AI помічник")
        self.ai_btn.clicked.connect(self._open_ai_assistant)
        actions_layout.addWidget(self.ai_btn)
        
        # Кнопка редагування
        self.edit_btn = TransparentToolButton(FIF.EDIT)
        self.edit_btn.setFixedSize(120, 120)
        self.edit_btn.setToolTip("Редагувати клієнта")
        self.edit_btn.setStyleSheet("""
            TransparentToolButton {
                background-color: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 60px;
            }
            TransparentToolButton:hover {
                background-color: rgba(59, 130, 246, 0.2);
                border: 1px solid rgba(59, 130, 246, 0.5);
            }
        """)
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.client_id))
        actions_layout.addWidget(self.edit_btn)
        
        # Кнопка видалення
        self.delete_btn = TransparentToolButton(FIF.DELETE)
        self.delete_btn.setFixedSize(120, 120)
        self.delete_btn.setToolTip("Видалити клієнта")
        self.delete_btn.setStyleSheet("""
            TransparentToolButton {
                background-color: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 60px;
            }
            TransparentToolButton:hover {
                background-color: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.client_id))
        actions_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(actions_layout)
        
    def _load_avatar(self):
        """Завантажує аватар клієнта"""
        photo_path = self.client_data.get('photo_path')
        
        if photo_path and os.path.exists(photo_path):
            # Завантажуємо реальне фото
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                # Обрізаємо в коло
                scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                
                # Створюємо кругову маску
                rounded_pixmap = QPixmap(60, 60)
                rounded_pixmap.fill(Qt.transparent)
                
                painter = QPainter(rounded_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                path = QPainterPath()
                path.addRoundedRect(0, 0, 60, 60, 30, 30)
                painter.setClipPath(path)
                
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()
                
                self.avatar.setPixmap(rounded_pixmap)
                return
        
        # Заглушка з іконкою користувача
        self.avatar.setText("👤")
        self.avatar.setStyleSheet("""
            QLabel {
                background-color: #e5e7eb;
                border: 2px solid #d1d5db;
                border-radius: 30px;
                font-size: 24px;
                color: #6b7280;
            }
        """)
    
    def _open_ai_assistant(self):
        """Відкриває персонального АІ помічника для клієнта"""
        # Отримуємо URL AI помічника з даних клієнта
        ai_url = self.client_data.get('ai_url', '').strip()
        
        if ai_url:
            # Якщо посилання збережено - відкриваємо браузер
            try:
                webbrowser.open(ai_url)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Помилка",
                    f"Не вдалося відкрити браузер:\n{str(e)}"
                )
        else:
            # Якщо посилання не налаштовано - показуємо інструкцію
            QMessageBox.information(
                self,
                "АІ помічник не налаштовано",
                "АІ помічник для цього клієнта ще не налаштований.\n\n"
                "Для налаштування:\n"
                "1. Відкрийте редагування клієнта\n"
                "2. Перейдіть на вкладку '🤖 Персональний АІ'\n"
                "3. Створіть та налаштуйте АІ помічника"
            )
    
    def _show_development_message(self, feature_name):
        """Показує повідомлення про розробку функції"""
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.warning(
            title='В розробці',
            content=f"Функція '{feature_name}' поки що в розробці",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.window()
        )
    
    def mousePressEvent(self, event):
        """Обробка кліку по елементу списку"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.client_id)
        super().mousePressEvent(event)
