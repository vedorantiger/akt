# ui/dialogs/edit_client/main_dialog.py
"""Головний діалог редагування клієнта"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QWidget, QFrame, QFileDialog)
from PySide6.QtGui import QFont
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition
from .basic_tab import BasicTab
from .physical_tab_new import PhysicalTab
from .health_tab import HealthTab
from .lifestyle_tab import LifestyleTab
from .goals_tab import GoalsTab
from .measurements_tab import MeasurementsTab
from .testing_tab import TestingTab
from .ai_tab import AITab
from ui.dialogs.photo_display import PhotoDisplayWidget
from ui.styles import COLORS
import os


class EditClientDialog(QDialog):
    """Діалог додавання/редагування клієнта"""
    
    client_saved = Signal(dict)  # Сигнал при збереженні клієнта
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data or {}
        self.is_edit_mode = bool(client_data)
        self._current_photo_path = self.client_data.get('photo_path')
        
        # Налаштування вікна
        self.setWindowTitle("✏️ Редагувати клієнта" if self.is_edit_mode else "➕ Додати клієнта")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        self._init_ui()
        
        # Заповнюємо дані якщо редагуємо
        if self.is_edit_mode:
            self._load_client_data()
        else:
            # Для нового клієнта очищаємо всі поля
            self._set_empty_values_for_new_client()
    
    def _init_ui(self):
        """Створює інтерфейс діалогу"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ===== ЛІВА ПАНЕЛЬ: ФОТО КЛІЄНТА =====
        self._create_photo_panel()
        
        # ===== ПРАВА ПАНЕЛЬ: ВКЛАДКИ З ДАНИМИ =====
        self._create_data_panel()
        
        # Додаємо панелі до основного layout
        main_layout.addWidget(self.photo_panel)
        main_layout.addWidget(self.data_panel, 1)  # Розтягується
    
    def _create_photo_panel(self):
        """Створює ліву панель для фото"""
        self.photo_panel = QFrame()
        self.photo_panel.setFixedWidth(320)
        self.photo_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        # Додаємо тінь
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.photo_panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.photo_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("📷 Фото клієнта")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title)
        
        # Область відображення фото
        self.photo_display = PhotoDisplayWidget()
        self.photo_display.setFixedSize(280, 350)
        layout.addWidget(self.photo_display)
        
        # Кнопка вибору фото
        self.select_photo_btn = QPushButton("📁 Обрати фото")
        self.select_photo_btn.setFixedHeight(45)
        self.select_photo_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton:hover {{
                background: #2563eb;
            }}
            QPushButton:pressed {{
                background: #1d4ed8;
            }}
        """)
        self.select_photo_btn.clicked.connect(self._select_photo)
        layout.addWidget(self.select_photo_btn)
        
        layout.addStretch()
    
    def _create_data_panel(self):
        """Створює праву панель з вкладками"""
        self.data_panel = QFrame()
        self.data_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self.data_panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("📋 Інформація про клієнта")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #111827;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title)
        
        # Створюємо вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: #F3F4F6;
                color: #6B7280;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: #E5E7EB;
            }}
        """)
        
        # Створюємо всі 8 вкладок
        self.basic_tab = BasicTab(self.client_data, parent=self)
        self.physical_tab = PhysicalTab(self.client_data, parent=self)
        self.health_tab = HealthTab(self.client_data)
        self.lifestyle_tab = LifestyleTab(self.client_data)
        self.goals_tab = GoalsTab(self.client_data)
        self.measurements_tab = MeasurementsTab(self.client_data)
        self.testing_tab = TestingTab(self.client_data)
        self.ai_tab = AITab(self.client_data)
        
        # Підключаємо сигнали для автоматичних розрахунків
        self._setup_tab_connections()
        
        # Додаємо вкладки
        self.tab_widget.addTab(self.basic_tab, "👤 Основні дані")
        self.tab_widget.addTab(self.physical_tab, "💪 Фізичні параметри")
        self.tab_widget.addTab(self.health_tab, "❤️ Здоров'я")
        self.tab_widget.addTab(self.lifestyle_tab, "🏃 Спосіб життя")
        self.tab_widget.addTab(self.goals_tab, "🎯 Цілі та плани")
        self.tab_widget.addTab(self.measurements_tab, "📏 Поточні заміри")
        self.tab_widget.addTab(self.testing_tab, "📸 Тестування")
        self.tab_widget.addTab(self.ai_tab, "🤖 Персональний АІ")
        
        layout.addWidget(self.tab_widget, 1)
        
        # Кнопки керування
        self._create_control_buttons(layout)
    
    def _create_control_buttons(self, layout):
        """Створює кнопки керування внизу вікна"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        
        buttons_layout.addStretch()
        
        # Кнопка скасування
        cancel_btn = QPushButton("❌ Скасувати")
        cancel_btn.setFixedSize(140, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #6B7280;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background: #4B5563;
            }
            QPushButton:pressed {
                background: #374151;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Кнопка збереження
        save_btn = QPushButton("✅ Зберегти")
        save_btn.setFixedSize(140, 45)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
            QPushButton:pressed {{
                background: #047857;
            }}
        """)
        save_btn.clicked.connect(self._save_client)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _setup_tab_connections(self):
        """Налаштовує зв'язки між вкладками для автоматичних розрахунків"""
        print("🔗 Налаштовую зв'язки між вкладками...")
        
        # Підключаємо зміни в основних даних (вік, стать) до оновлення розрахунків
        if hasattr(self.basic_tab, 'birth_date_edit'):
            self.basic_tab.birth_date_edit.dateChanged.connect(self._trigger_calculations_update)
            print("✅ Підключено сигнал dateChanged для дати народження")
        
        if hasattr(self.basic_tab, 'gender_combo'):
            self.basic_tab.gender_combo.currentTextChanged.connect(self._trigger_calculations_update)
            print("✅ Підключено сигнал currentTextChanged для статі")
        
        # Підключаємо зміни в способі життя (активність) до оновлення розрахунків
        if hasattr(self.lifestyle_tab, 'activity_level_combo'):
            self.lifestyle_tab.activity_level_combo.currentTextChanged.connect(self._trigger_calculations_update)
            print("✅ Підключено сигнал currentTextChanged для рівня активності")
        
        print("🔗 Зв'язки між вкладками налаштовано")
    
    def _trigger_calculations_update(self):
        """Запускає оновлення розрахунків у фізичній вкладці"""
        print("🔥 Запуск оновлення розрахунків...")
        
        # Перевіряємо чи існує physical_tab
        if not hasattr(self, 'physical_tab'):
            print("⚠️ physical_tab ще не створено")
            return
            
        if hasattr(self.physical_tab, '_update_calculations'):
            print("📊 Викликаю _update_calculations в physical_tab")
            self.physical_tab._update_calculations()
        else:
            print("⚠️ Метод _update_calculations не знайдено в physical_tab")
    
    def _select_photo(self):
        """Відкриває діалог вибору фото"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Оберіть фото клієнта",
            "",
            "Зображення (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            self._current_photo_path = file_path
            self.photo_display.load_photo(file_path)
            
            InfoBar.success(
                title="Успіх",
                content="Фото успішно завантажено",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def _load_client_data(self):
        """Завантажує дані клієнта для редагування"""
        if self.is_edit_mode and self.client_data:
            # Встановлюємо параметри фото
            photo_params = {
                'photo_path': self.client_data.get('photo_path'),
                'photo_scale': self.client_data.get('photo_scale', 1.0),
                'photo_offset_x': self.client_data.get('photo_offset_x', 0),
                'photo_offset_y': self.client_data.get('photo_offset_y', 0),
                'brightness': self.client_data.get('brightness', 0),
                'contrast': self.client_data.get('contrast', 0),
                'saturation': self.client_data.get('saturation', 0),
                'sharpness': self.client_data.get('sharpness', 0)
            }
            self.photo_display.set_photo_params(photo_params)
        elif self._current_photo_path:
            self.photo_display.load_photo(self._current_photo_path)
    
    def _save_client(self):
        """Збереження клієнта"""
        try:
            # Збираємо дані з усіх вкладок
            client_data = {}
            
            # Основні дані (обов'язкові)
            basic_data = self.basic_tab.get_data()
            if not self._validate_required_fields(basic_data):
                return
            
            client_data.update(basic_data)
            client_data.update(self.physical_tab.get_data())
            client_data.update(self.health_tab.get_data())
            client_data.update(self.lifestyle_tab.get_data())
            client_data.update(self.goals_tab.get_data())
            client_data.update(self.measurements_tab.get_data())
            client_data.update(self.testing_tab.get_data())
            client_data.update(self.ai_tab.get_data())
            
            # Додаємо фото та його параметри
            client_data['photo_path'] = self._current_photo_path
            
            # Зберігаємо параметри позиціонування фото
            photo_params = self.photo_display.get_current_transform_params()
            client_data.update(photo_params)
            
            # Додаємо мета-дані
            from datetime import datetime
            if not self.is_edit_mode:
                import uuid
                client_data['id'] = str(uuid.uuid4())
                client_data['created_at'] = datetime.now().isoformat()
                client_data['last_visit'] = datetime.now().strftime("%d.%m.%Y")
            else:
                client_data['id'] = self.client_data.get('id')
                client_data['created_at'] = self.client_data.get('created_at')
                client_data['last_visit'] = datetime.now().strftime("%d.%m.%Y")
            
            client_data['updated_at'] = datetime.now().isoformat()
            
            # Зберігаємо клієнта у файл JSON (тимчасово, поки немає БД)
            self._save_client_to_file(client_data)
            
            self.client_saved.emit(client_data)
            
            InfoBar.success(
                title="Успіх",
                content="Клієнта успішно збережено",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            
            self.accept()
            
        except Exception as e:
            MessageBox(
                title="❌ Помилка збереження",
                content=f"Виникла помилка при збереженні клієнта:\n\n{str(e)}\n\nПеревірте правильність введених даних.",
                parent=self
            ).exec()
    
    def _validate_required_fields(self, basic_data):
        """Перевіряє обов'язкові поля"""
        # Перевіряємо ім'я та прізвище (основні обов'язкові поля)
        first_name = basic_data.get('first_name', '').strip()
        surname = basic_data.get('surname', '').strip()
        
        if not first_name:
            MessageBox(
                title="⚠️ Необхідні дані",
                content="Поле 'Ім'я' є обов'язковим для заповнення.\n\nВведіть ім'я клієнта перед збереженням.",
                parent=self
            ).exec()
            
            # Переключаємося на вкладку з основними даними
            self.tab_widget.setCurrentIndex(0)
            self.basic_tab.first_name_edit.setFocus()
            return False
        
        if not surname:
            MessageBox(
                title="⚠️ Необхідні дані",
                content="Поле 'Прізвище' є обов'язковим для заповнення.\n\nВведіть прізвище клієнта перед збереженням.",
                parent=self
            ).exec()
            
            # Переключаємося на вкладку з основними даними
            self.tab_widget.setCurrentIndex(0)
            self.basic_tab.surname_edit.setFocus()
            return False
        
        # Перевіряємо мінімальну довжину імені та прізвища
        if len(first_name) < 2:
            MessageBox(
                title="⚠️ Некоректні дані",
                content="Ім'я клієнта повинно містити принаймні 2 символи.\n\nВведіть коректне ім'я.",
                parent=self
            ).exec()
            
            self.tab_widget.setCurrentIndex(0)
            self.basic_tab.first_name_edit.setFocus()
            return False
        
        if len(surname) < 2:
            MessageBox(
                title="⚠️ Некоректні дані",
                content="Прізвище клієнта повинно містити принаймні 2 символи.\n\nВведіть коректне прізвище.",
                parent=self
            ).exec()
            
            self.tab_widget.setCurrentIndex(0)
            self.basic_tab.surname_edit.setFocus()
            return False
        
        return True
    
    def _save_client_to_file(self, client_data):
        """Зберігає клієнта у файл JSON"""
        import json
        import os
        from datetime import datetime
        
        # Створюємо папку для клієнтів якщо її немає
        clients_dir = "data/clients"
        os.makedirs(clients_dir, exist_ok=True)
        
        # Додаємо timestamp
        client_data['created_at'] = datetime.now().isoformat()
        client_data['updated_at'] = datetime.now().isoformat()
        
        # Створюємо безпечне ім'я файлу з імені та прізвища
        first_name = client_data.get('first_name', '')
        surname = client_data.get('surname', '')
        full_name = f"{first_name} {surname}".strip()
        
        safe_name = "".join(c for c in full_name if c.isalnum() or c in ' -_').strip()
        safe_name = safe_name.replace(' ', '_')[:30]  # Обмежуємо довжину
        
        filename = f"{safe_name}_{client_data['id'][:8]}.json"
        filepath = os.path.join(clients_dir, filename)
        
        # Зберігаємо у файл
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(client_data, f, ensure_ascii=False, indent=2)
        
        # Виводимо повідомлення про успішне збереження
        from config.logger import get_app_logger
        logger = get_app_logger()
        
        logger.info(f"💾 Клієнта '{full_name}' збережено: {filename}")
        print(f"✅ Клієнта збережено: {filepath}")
        
        return client_data
    
    def _set_empty_values_for_new_client(self):
        """Встановлює пусті значення для всіх полів при створенні нового клієнта"""
        print("🆕 Встановлення пустих значень для нового клієнта...")
        
        # Очищаємо поля в basic_tab
        if hasattr(self, 'basic_tab') and hasattr(self.basic_tab, 'set_default_empty_values'):
            self.basic_tab.set_default_empty_values()
        
        # Очищаємо поля в physical_tab - там вже встановлені нульові значення
        print("✅ Всі поля очищені для нового клієнта")
