# ui/dialogs/edit_client/ai_tab.py
"""Вкладка персонального АІ клієнта"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                               QPushButton, QScrollArea, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from qfluentwidgets import LineEdit, TextEdit, InfoBar, InfoBarPosition
from ui.styles import COLORS
from utils.ai_helper import generate_ai_prompt, get_default_ai_url
import webbrowser


class AITab(QWidget):
    """Вкладка персонального АІ клієнта"""
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data or {}
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Створює інтерфейс вкладки"""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        content_layout = QVBoxLayout(main_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # ===== НАЛАШТУВАННЯ АІ =====
        ai_setup_group = QGroupBox("🤖 Налаштування персонального АІ")
        ai_setup_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(ai_setup_group)
        
        ai_setup_layout = QVBoxLayout(ai_setup_group)
        ai_setup_layout.setContentsMargins(20, 25, 20, 20)
        ai_setup_layout.setSpacing(15)
        
        # Інструкції
        instructions_label = QLabel("""
<b>🎯 Як створити персонального АІ-помічника:</b><br>
1️⃣ Натисніть "Скопіювати промт для АІ" щоб скопіювати всі дані клієнта<br>
2️⃣ Натисніть "Відкрити сторінку АІ" для переходу до Google AI Studio<br>
3️⃣ Створіть новий чат та вставте скопійований промт<br>
4️⃣ Збережіть посилання на створений чат у поле нижче<br>
5️⃣ Тепер у вас є персональний АІ-помічник для цього клієнта! 🎉
        """)
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("""
            QLabel {
                background: #F0F9FF;
                border: 2px solid #0EA5E9;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                color: #0C4A6E;
                line-height: 1.5;
            }
        """)
        ai_setup_layout.addWidget(instructions_label)
        
        # Кнопки дій
        buttons_layout = QHBoxLayout()
        
        self.copy_prompt_btn = QPushButton("📋 Скопіювати промт для АІ")
        self.copy_prompt_btn.setFixedHeight(45)
        self.copy_prompt_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background: #2563eb;
            }}
        """)
        self.copy_prompt_btn.clicked.connect(self._copy_ai_prompt)
        
        self.open_ai_btn = QPushButton("🌐 Відкрити сторінку АІ")
        self.open_ai_btn.setFixedHeight(45)
        self.open_ai_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """)
        self.open_ai_btn.clicked.connect(self._open_ai_page)
        
        buttons_layout.addWidget(self.copy_prompt_btn)
        buttons_layout.addWidget(self.open_ai_btn)
        buttons_layout.addStretch()
        
        ai_setup_layout.addLayout(buttons_layout)
        
        # Поле для збереження посилання на АІ
        self.ai_link_edit = LineEdit()
        self.ai_link_edit.setPlaceholderText("Вставте сюди посилання на створений АІ-чат")
        self.ai_link_edit.setMinimumHeight(45)
        ai_setup_layout.addWidget(self.ai_link_edit)
        
        # ===== ПРОМТ ДЛЯ АІ =====
        prompt_group = QGroupBox("📝 Промт для АІ (попередній перегляд)")
        prompt_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(prompt_group)
        
        prompt_layout = QVBoxLayout(prompt_group)
        prompt_layout.setContentsMargins(20, 25, 20, 20)
        
        self.ai_prompt_preview = TextEdit()
        self.ai_prompt_preview.setReadOnly(True)
        self.ai_prompt_preview.setMinimumHeight(300)
        self.ai_prompt_preview.setStyleSheet("""
            QTextEdit {
                background: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: #374151;
                padding: 12px;
            }
        """)
        prompt_layout.addWidget(self.ai_prompt_preview)
        
        content_layout.addStretch()
        
        # Генеруємо промт при ініціалізації
        self._generate_ai_prompt()
    
    def _get_group_style(self):
        """Повертає стиль для групи"""
        return """
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #111827;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
    
    def _generate_ai_prompt(self):
        """Генерує промт для АІ на основі даних клієнта"""
        prompt = generate_ai_prompt(self.client_data)
        self.ai_prompt_preview.setText(prompt)
        return prompt
    
    def _copy_ai_prompt(self):
        """Копіює промт в буфер обміну"""
        from PySide6.QtWidgets import QApplication
        
        prompt = self._generate_ai_prompt()
        clipboard = QApplication.clipboard()
        clipboard.setText(prompt)
        
        InfoBar.success(
            title="✅ Промт скопійовано",
            content="Промт для АІ скопійовано в буфер обміну",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def _open_ai_page(self):
        """Відкриває сторінку Google AI Studio або збережене посилання"""
        ai_link = self.ai_link_edit.text().strip()
        
        if ai_link:
            # Відкриваємо збережене посилання
            webbrowser.open(ai_link)
            InfoBar.info(
                title="Відкрито",
                content="Відкрито збережений АІ-чат",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            # Відкриваємо Google AI Studio
            webbrowser.open("https://aistudio.google.com/app/prompts/new_chat")
            InfoBar.info(
                title="Відкрито",
                content="Відкрито Google AI Studio",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def _load_data(self):
        """Завантажує дані клієнта"""
        if not self.client_data:
            return
        
        # Завантажуємо посилання на АІ
        self.ai_link_edit.setText(self.client_data.get('ai_url', ''))
        
        # Оновлюємо промт з новими даними
        self._generate_ai_prompt()
    
    def get_data(self):
        """Повертає дані вкладки"""
        return {
            'ai_url': self.ai_link_edit.text().strip()
        }
