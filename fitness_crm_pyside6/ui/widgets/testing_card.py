# ui/widgets/testing_card.py
"""Картка фотографії тестування"""
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QCheckBox, QFrame)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont


class TestingPhotoCard(QWidget):
    """Картка фотографії тестування"""
    
    # Сигнали
    selection_changed = Signal(bool, str)  # (вибрано, шлях_до_фото)
    delete_requested = Signal(str)  # шлях_до_фото
    edit_requested = Signal(str)  # шлях_до_фото
    
    def __init__(self, photo_path, date_taken="", description="", parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.date_taken = date_taken
        self.description = description
        self.is_selected = False
        
        self.setFixedSize(280, 380)
        self._init_ui()
        self._load_photo()
    
    def _init_ui(self):
        """Створює інтерфейс картки"""
        # Основний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Рамка картки
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #3B82F6;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
            }
        """)
        main_layout.addWidget(self.card_frame)
        
        # Layout для вмісту картки
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # Верхня панель з чекбоксом
        top_layout = QHBoxLayout()
        
        self.select_checkbox = QCheckBox("Вибрати")
        self.select_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #374151;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #D1D5DB;
                border-radius: 3px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #3B82F6;
                border-color: #3B82F6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)
        self.select_checkbox.toggled.connect(self._on_selection_changed)
        
        top_layout.addWidget(self.select_checkbox)
        top_layout.addStretch()
        
        card_layout.addLayout(top_layout)
        
        # Зображення
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(240, 240)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #F9FAFB;
            }
        """)
        card_layout.addWidget(self.photo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Інформація про фото
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Дата
        self.date_label = QLabel(self.date_taken or "Без дати")
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6B7280;
                font-weight: 500;
                border: none;
                background: transparent;
            }
        """)
        info_layout.addWidget(self.date_label)
        
        # Опис
        self.description_label = QLabel(self.description or "Без опису")
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumHeight(40)
        self.description_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #374151;
                border: none;
                background: transparent;
            }
        """)
        info_layout.addWidget(self.description_label)
        
        card_layout.addLayout(info_layout)
        
        # Кнопки дій
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setFixedSize(30, 24)
        self.edit_btn.setToolTip("Редагувати інформацію")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #E5E7EB;
                border-color: #9CA3AF;
            }
        """)
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.photo_path))
        
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(30, 24)
        self.delete_btn.setToolTip("Видалити фото")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #FEE2E2;
                border-color: #F87171;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.photo_path))
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        
        card_layout.addLayout(buttons_layout)
    
    def _load_photo(self):
        """Завантажує та відображає фото"""
        if not os.path.exists(self.photo_path):
            self.photo_label.setText("📷\nФото не знайдено")
            self.photo_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    background: #F9FAFB;
                    color: #9CA3AF;
                    font-size: 14px;
                }
            """)
            return
        
        pixmap = QPixmap(self.photo_path)
        if not pixmap.isNull():
            # Масштабуємо зображення зберігаючи пропорції
            scaled_pixmap = pixmap.scaled(
                238, 238,  # -2px для рамки
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled_pixmap)
        else:
            self.photo_label.setText("📷\nПомилка завантаження")
    
    def _on_selection_changed(self, checked):
        """Обробляє зміну вибору картки"""
        self.is_selected = checked
        self.selection_changed.emit(checked, self.photo_path)
        
        # Змінюємо стиль рамки в залежності від вибору
        if checked:
            self.card_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 3px solid #3B82F6;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
                }
            """)
        else:
            self.card_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 2px solid #E5E7EB;
                    border-radius: 12px;
                }
                QFrame:hover {
                    border-color: #3B82F6;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                }
            """)
    
    def set_selected(self, selected):
        """Встановлює стан вибору"""
        self.select_checkbox.setChecked(selected)
    
    def update_info(self, date_taken, description):
        """Оновлює інформацію про фото"""
        self.date_taken = date_taken
        self.description = description
        self.date_label.setText(date_taken or "Без дати")
        self.description_label.setText(description or "Без опису")


class TestingTextCard(QWidget):
    """Картка текстового блоку тестування"""
    
    # Сигнали
    delete_requested = Signal(int)  # індекс
    edit_requested = Signal(int)  # індекс
    
    def __init__(self, index, date_created="", text_content="", parent=None):
        super().__init__(parent)
        self.index = index
        self.date_created = date_created
        self.text_content = text_content
        
        self.setMinimumHeight(120)
        self.setMaximumHeight(180)
        self._init_ui()
    
    def _init_ui(self):
        """Створює інтерфейс картки"""
        # Основний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Рамка картки
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #8B5CF6;
            }
        """)
        main_layout.addWidget(self.card_frame)
        
        # Layout для вмісту картки
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # Заголовок з датою
        header_layout = QHBoxLayout()
        
        self.date_label = QLabel(f"📝 {self.date_created}")
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #6B7280;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)
        
        # Кнопки дій
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setFixedSize(24, 24)
        self.edit_btn.setToolTip("Редагувати")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #E5E7EB;
            }
        """)
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.index))
        
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setToolTip("Видалити")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #FEE2E2;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        
        header_layout.addWidget(self.date_label)
        header_layout.addStretch()
        header_layout.addWidget(self.edit_btn)
        header_layout.addWidget(self.delete_btn)
        
        card_layout.addLayout(header_layout)
        
        # Текстовий вміст
        self.content_label = QLabel(self.text_content)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #374151;
                border: none;
                background: transparent;
                padding: 8px;
                background: #F9FAFB;
                border-radius: 6px;
            }
        """)
        card_layout.addWidget(self.content_label)
    
    def update_content(self, date_created, text_content):
        """Оновлює вміст картки"""
        self.date_created = date_created
        self.text_content = text_content
        self.date_label.setText(f"📝 {date_created}")
        self.content_label.setText(text_content)
