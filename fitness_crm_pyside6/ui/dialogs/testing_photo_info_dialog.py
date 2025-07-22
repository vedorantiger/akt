# ui/dialogs/testing_photo_info_dialog.py
"""Діалог для додавання інформації про фото тестування"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTextEdit, QDateEdit, QFrame)
from PySide6.QtCore import Qt, QDate
from qfluentwidgets import MessageBox


class TestingPhotoInfoDialog(QDialog):
    """Діалог для введення інформації про фото тестування"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_taken = ""
        self.description = ""
        self._init_ui()
    
    def _init_ui(self):
        """Створює інтерфейс діалогу"""
        self.setWindowTitle("📸 Інформація про фото тестування")
        self.setFixedSize(400, 280)
        self.setModal(True)
        
        # Основний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Додати інформацію про фото")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Рамка з полями
        fields_frame = QFrame()
        fields_frame.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        main_layout.addWidget(fields_frame)
        
        fields_layout = QVBoxLayout(fields_frame)
        fields_layout.setSpacing(12)
        
        # Дата зйомки
        date_layout = QVBoxLayout()
        date_layout.setSpacing(6)
        
        date_label = QLabel("📅 Дата зйомки:")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
            }
        """)
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                font-size: 13px;
                padding: 8px 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background: white;
            }
            QDateEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        date_layout.addWidget(self.date_edit)
        
        fields_layout.addLayout(date_layout)
        
        # Опис
        description_layout = QVBoxLayout()
        description_layout.setSpacing(6)
        
        description_label = QLabel("📝 Опис фото:")
        description_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
            }
        """)
        description_layout.addWidget(description_label)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Наприклад: Вигляд спереду, Після 3 місяців тренувань...")
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                padding: 8px 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background: white;
            }
            QTextEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        description_layout.addWidget(self.description_edit)
        
        fields_layout.addLayout(description_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Скасувати")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F3F4F6;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #E5E7EB;
                border-color: #9CA3AF;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("✅ Зберегти")
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        ok_btn.clicked.connect(self._save_info)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _save_info(self):
        """Зберігає інформацію та закриває діалог"""
        description = self.description_edit.toPlainText().strip()
        
        if not description:
            MessageBox.warning(
                title="Помилка",
                content="Будь ласка, додайте опис фото",
                parent=self
            )
            return
        
        # Зберігаємо дані
        self.date_taken = self.date_edit.date().toString("dd.MM.yyyy")
        self.description = description
        
        self.accept()
    
    def get_info(self):
        """Повертає введену інформацію"""
        return self.date_taken, self.description


class TestingTextInfoDialog(QDialog):
    """Діалог для додавання/редагування текстового блоку"""
    
    def __init__(self, date_created="", text_content="", parent=None):
        super().__init__(parent)
        self.date_created = date_created
        self.text_content = text_content
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Створює інтерфейс діалогу"""
        self.setWindowTitle("📝 Текстовий блок тестування")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        # Основний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Додати текстовий блок")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Рамка з полями
        fields_frame = QFrame()
        fields_frame.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        main_layout.addWidget(fields_frame)
        
        fields_layout = QVBoxLayout(fields_frame)
        fields_layout.setSpacing(12)
        
        # Дата створення
        date_layout = QVBoxLayout()
        date_layout.setSpacing(6)
        
        date_label = QLabel("📅 Дата створення:")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
            }
        """)
        date_layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                font-size: 13px;
                padding: 8px 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background: white;
            }
            QDateEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        date_layout.addWidget(self.date_edit)
        
        fields_layout.addLayout(date_layout)
        
        # Текстовий вміст
        content_layout = QVBoxLayout()
        content_layout.setSpacing(6)
        
        content_label = QLabel("📄 Текстовий вміст:")
        content_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
            }
        """)
        content_layout.addWidget(content_label)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Наприклад: Результати фізичних тестів, спостереження тренера...")
        self.content_edit.setMinimumHeight(140)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background: white;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        content_layout.addWidget(self.content_edit)
        
        fields_layout.addLayout(content_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Скасувати")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F3F4F6;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #E5E7EB;
                border-color: #9CA3AF;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("✅ Зберегти")
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #8B5CF6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #7C3AED;
            }
        """)
        ok_btn.clicked.connect(self._save_content)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _load_data(self):
        """Завантажує існуючі дані"""
        if self.date_created:
            try:
                date_parts = self.date_created.split('.')
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    self.date_edit.setDate(QDate(year, month, day))
            except:
                pass
        
        if self.text_content:
            self.content_edit.setText(self.text_content)
    
    def _save_content(self):
        """Зберігає вміст та закриває діалог"""
        content = self.content_edit.toPlainText().strip()
        
        if not content:
            MessageBox.warning(
                title="Помилка",
                content="Будь ласка, додайте текстовий вміст",
                parent=self
            )
            return
        
        # Зберігаємо дані
        self.date_created = self.date_edit.date().toString("dd.MM.yyyy")
        self.text_content = content
        
        self.accept()
    
    def get_content(self):
        """Повертає введений вміст"""
        return self.date_created, self.text_content
