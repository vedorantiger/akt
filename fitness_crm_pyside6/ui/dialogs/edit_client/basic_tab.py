# ui/dialogs/edit_client/basic_tab.py
"""Вкладка основних даних клієнта"""
from PySide6 import QtWidgets
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QComboBox, QDateEdit, QTextEdit, QGroupBox)
from qfluentwidgets import LineEdit, ComboBox, DateEdit, TextEdit
import re


class BasicTab(QWidget):
    """Вкладка основних даних клієнта"""
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data or {}
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Створює інтерфейс вкладки"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ===== ОСНОВНА ІНФОРМАЦІЯ =====
        main_group = QGroupBox("👤 Основна інформація")
        main_group.setStyleSheet("""
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
        """)
        main_layout.addWidget(main_group)
        
        main_form = QFormLayout(main_group)
        main_form.setSpacing(15)
        main_form.setContentsMargins(20, 25, 20, 20)
        
        # Прізвище (обов'язкове)
        self.surname_edit = LineEdit()
        self.surname_edit.setPlaceholderText("Введіть прізвище клієнта *")
        self.surname_edit.setMinimumHeight(40)
        self.surname_edit.setStyleSheet("""
            LineEdit {
                border: 2px solid #FEE2E2;
                background: #FEF2F2;
            }
            LineEdit:focus {
                border: 2px solid #3B82F6;
                background: white;
            }
        """)
        self.surname_edit.textChanged.connect(self._on_surname_changed)
        main_form.addRow("📝 Прізвище *:", self.surname_edit)
        
        # Ім'я (обов'язкове)
        self.first_name_edit = LineEdit()
        self.first_name_edit.setPlaceholderText("Введіть ім'я клієнта *")
        self.first_name_edit.setMinimumHeight(40)
        self.first_name_edit.setStyleSheet("""
            LineEdit {
                border: 2px solid #FEE2E2;
                background: #FEF2F2;
            }
            LineEdit:focus {
                border: 2px solid #3B82F6;
                background: white;
            }
        """)
        self.first_name_edit.textChanged.connect(self._on_name_changed)
        main_form.addRow("📝 Ім'я *:", self.first_name_edit)
        
        # Телефон (рекомендований)
        self.phone_edit = LineEdit()
        self.phone_edit.setPlaceholderText("+380 XX XXX XX XX")
        self.phone_edit.setMinimumHeight(40)
        self.phone_edit.textChanged.connect(self._format_phone)
        main_form.addRow("📞 Телефон:", self.phone_edit)
        
        # Email
        self.email_edit = LineEdit()
        self.email_edit.setPlaceholderText("example@email.com")
        self.email_edit.setMinimumHeight(40)
        main_form.addRow("📧 Email:", self.email_edit)
        
        # Запасний телефон
        self.spare_phone_edit = LineEdit()
        self.spare_phone_edit.setPlaceholderText("+380 XX XXX XX XX")
        self.spare_phone_edit.setMinimumHeight(40)
        self.spare_phone_edit.textChanged.connect(self._format_spare_phone)
        main_form.addRow("📱 Запасний телефон:", self.spare_phone_edit)
        
        # ===== ПЕРСОНАЛЬНІ ДАНІ =====
        personal_group = QGroupBox("🆔 Персональні дані")
        personal_group.setStyleSheet(main_group.styleSheet())
        main_layout.addWidget(personal_group)
        
        personal_form = QFormLayout(personal_group)
        personal_form.setSpacing(15)
        personal_form.setContentsMargins(20, 25, 20, 20)
        
        # Дата народження
        self.birth_date_edit = DateEdit()
        self.birth_date_edit.setDate(QDate(1900, 1, 1))  # Мінімальна дата - користувач сам введе
        self.birth_date_edit.setMinimumHeight(40)
        # Сигнал для автоматичних розрахунків
        self.birth_date_edit.dateChanged.connect(self._on_birth_date_changed)
        personal_form.addRow("🎂 Дата народження:", self.birth_date_edit)
        
        # Стать
        self.gender_combo = ComboBox()
        self.gender_combo.addItems(["Оберіть стать", "Чоловік", "Жінка"])
        self.gender_combo.setMinimumHeight(40)
        # Сигнал для автоматичних розрахунків
        self.gender_combo.currentTextChanged.connect(self._on_gender_changed)
        personal_form.addRow("⚧ Стать:", self.gender_combo)
        
        # Рід занять
        self.occupation_edit = LineEdit()
        self.occupation_edit.setPlaceholderText("Професія, посада")
        self.occupation_edit.setMinimumHeight(40)
        personal_form.addRow("💼 Рід занять:", self.occupation_edit)
        
        # ===== АДРЕСА ТА КОНТАКТИ =====
        address_group = QGroupBox("🏠 Адреса та контакти")
        address_group.setStyleSheet(main_group.styleSheet())
        main_layout.addWidget(address_group)
        
        address_form = QFormLayout(address_group)
        address_form.setSpacing(15)
        address_form.setContentsMargins(20, 25, 20, 20)
        
        # Адреса
        self.address_edit = TextEdit()
        self.address_edit.setPlaceholderText("Місто, вулиця, будинок, квартира")
        self.address_edit.setMaximumHeight(80)
        address_form.addRow("🗺️ Адреса:", self.address_edit)
        
        # Екстрений контакт
        emergency_layout = QVBoxLayout()
        
        self.emergency_name_edit = LineEdit()
        self.emergency_name_edit.setPlaceholderText("Ім'я контактної особи")
        self.emergency_name_edit.setMinimumHeight(40)
        emergency_layout.addWidget(self.emergency_name_edit)
        
        self.emergency_phone_edit = LineEdit()
        self.emergency_phone_edit.setPlaceholderText("+380 XX XXX XX XX")
        self.emergency_phone_edit.setMinimumHeight(40)
        self.emergency_phone_edit.textChanged.connect(self._format_emergency_phone)
        emergency_layout.addWidget(self.emergency_phone_edit)
        
        address_form.addRow("🚨 Екстрений контакт:", emergency_layout)
        
        main_layout.addStretch()
    
    def _on_name_changed(self):
        """Обробляє зміну імені - змінює стиль поля"""
        text = self.first_name_edit.text().strip()
        
        if len(text) >= 2:
            # Ім'я введено правильно - зелений стиль
            self.first_name_edit.setStyleSheet("""
                LineEdit {
                    border: 2px solid #D1FAE5;
                    background: #F0FDF4;
                }
                LineEdit:focus {
                    border: 2px solid #10B981;
                    background: white;
                }
            """)
        elif len(text) > 0:
            # Ім'я занадто коротке - жовтий стиль
            self.first_name_edit.setStyleSheet("""
                LineEdit {
                    border: 2px solid #FEF3C7;
                    background: #FFFBEB;
                }
                LineEdit:focus {
                    border: 2px solid #F59E0B;
                    background: white;
                }
            """)
        else:
            # Ім'я не введено - червоний стиль
            self.first_name_edit.setStyleSheet("""
                LineEdit {
                    border: 2px solid #FEE2E2;
                    background: #FEF2F2;
                }
                LineEdit:focus {
                    border: 2px solid #EF4444;
                    background: white;
                }
            """)
    
    def _format_phone(self):
        """Форматує основний телефон"""
        self._format_phone_field(self.phone_edit)
    
    def _format_spare_phone(self):
        """Форматує запасний телефон"""
        self._format_phone_field(self.spare_phone_edit)
    
    def _format_emergency_phone(self):
        """Форматує екстрений телефон"""
        self._format_phone_field(self.emergency_phone_edit)
    
    def _format_phone_field(self, field):
        """Універсальне форматування телефону"""
        text = field.text()
        # Видаляємо все крім цифр та +
        digits = re.sub(r'[^\d+]', '', text)
        
        # Якщо користувач вводить з +380
        if digits.startswith('+380'):
            # Залишаємо як є і форматуємо
            clean_digits = digits[4:]  # Видаляємо +380
        elif digits.startswith('380'):
            clean_digits = digits[3:]  # Видаляємо 380
        elif digits.startswith('0'):
            clean_digits = digits[1:]  # Видаляємо перший 0
        else:
            clean_digits = digits
        
        # Форматуємо номер залежно від довжини
        if len(clean_digits) == 0:
            formatted = ""
        elif len(clean_digits) <= 2:
            formatted = f"+380 {clean_digits}"
        elif len(clean_digits) <= 5:
            formatted = f"+380 {clean_digits[:2]} {clean_digits[2:]}"
        elif len(clean_digits) <= 7:
            formatted = f"+380 {clean_digits[:2]} {clean_digits[2:5]} {clean_digits[5:]}"
        elif len(clean_digits) <= 9:
            formatted = f"+380 {clean_digits[:2]} {clean_digits[2:5]} {clean_digits[5:7]} {clean_digits[7:]}"
        else:
            # Дозволяємо більше 9 цифр для міжнародних номерів
            formatted = f"+380 {clean_digits[:2]} {clean_digits[2:5]} {clean_digits[5:7]} {clean_digits[7:9]}"
            if len(clean_digits) > 9:
                formatted += f" {clean_digits[9:]}"
        
        # Встановлюємо курсор в кінець після форматування
        cursor_pos = len(formatted)
        field.blockSignals(True)
        field.setText(formatted)
        field.setCursorPosition(cursor_pos)
        field.blockSignals(False)
    
    def _on_surname_changed(self):
        """Обробляє зміну прізвища"""
        text = self.surname_edit.text().strip()
        if text:
            # Прізвище введено - зелений стиль
            self.surname_edit.setStyleSheet("""
                LineEdit {
                    border: 2px solid #D1FAE5;
                    background: #ECFDF5;
                }
                LineEdit:focus {
                    border: 2px solid #10B981;
                    background: white;
                }
            """)
        else:
            # Прізвище не введено - червоний стиль
            self.surname_edit.setStyleSheet("""
                LineEdit {
                    border: 2px solid #FEE2E2;
                    background: #FEF2F2;
                }
                LineEdit:focus {
                    border: 2px solid #EF4444;
                    background: white;
                }
            """)
    
    def _load_data(self):
        """Завантажує дані клієнта"""
        if not self.client_data:
            return
        
        # Завантажуємо окремі поля
        self.surname_edit.setText(self.client_data.get('surname', ''))
        self.first_name_edit.setText(self.client_data.get('first_name', ''))
        
        # Якщо немає окремих полів, але є full_name, спробуємо розділити
        if not self.client_data.get('surname') and not self.client_data.get('first_name'):
            full_name = self.client_data.get('full_name', '')
            if full_name:
                parts = full_name.split(' ', 1)
                if len(parts) >= 2:
                    self.first_name_edit.setText(parts[0])
                    self.surname_edit.setText(parts[1])
                elif len(parts) == 1:
                    self.first_name_edit.setText(parts[0])
        
        self.phone_edit.setText(self.client_data.get('phone', ''))
        self.email_edit.setText(self.client_data.get('email', ''))
        self.spare_phone_edit.setText(self.client_data.get('spare_phone', ''))
        self.occupation_edit.setText(self.client_data.get('occupation', ''))
        self.address_edit.setText(self.client_data.get('address', ''))
        self.emergency_name_edit.setText(self.client_data.get('emergency_name', ''))
        self.emergency_phone_edit.setText(self.client_data.get('emergency_phone', ''))
        
        # Дата народження
        if 'birth_date' in self.client_data:
            try:
                birth_date = QDate.fromString(self.client_data['birth_date'], "yyyy-MM-dd")
                self.birth_date_edit.setDate(birth_date)
            except:
                pass
        
        # Стать
        gender = self.client_data.get('gender', '')
        if gender in ['Чоловік', 'Жінка']:
            self.gender_combo.setCurrentText(gender)
        
        # Оновлюємо стиль поля імені
        self._on_name_changed()
    
    def get_data(self):
        """Повертає дані вкладки"""
        # Формуємо повне ім'я з прізвища та імені
        surname = self.surname_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        full_name = f"{first_name} {surname}".strip()
        
        return {
            'surname': surname,
            'first_name': first_name,
            'full_name': full_name,  # Для зворотної сумісності
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'spare_phone': self.spare_phone_edit.text().strip(),
            'birth_date': self.birth_date_edit.date().toString("yyyy-MM-dd"),
            'gender': self.gender_combo.currentText() if self.gender_combo.currentIndex() > 0 else '',
            'occupation': self.occupation_edit.text().strip(),
            'address': self.address_edit.toPlainText().strip(),
            'emergency_name': self.emergency_name_edit.text().strip(),
            'emergency_phone': self.emergency_phone_edit.text().strip()
        }
    
    def _on_birth_date_changed(self):
        """Обробник зміни дати народження для автоматичних розрахунків"""
        print(f"🎂 Дата народження змінена на: {self.birth_date_edit.date().toString('yyyy-MM-dd')}")
        self._trigger_auto_calculations()
    
    def _on_gender_changed(self, gender):
        """Обробник зміни статі для автоматичних розрахунків"""
        if gender and gender != "Оберіть стать":
            print(f"⚧ Стать вибрана: {gender}")
            self._trigger_auto_calculations()
    
    def _trigger_auto_calculations(self):
        """Запускає автоматичні розрахунки якщо є всі необхідні дані"""
        # Перевіряємо чи є дата народження та стать
        birth_date = self.birth_date_edit.date()
        gender = self.gender_combo.currentText()
        
        # Перевіряємо чи дата народження реально введена (не мінімальна)
        is_valid_date = birth_date.isValid() and birth_date.year() > 1950
        is_valid_gender = gender and gender != "Оберіть стать"
        
        if is_valid_date and is_valid_gender:
            print(f"✅ Всі дані для розрахунків є! Дата: {birth_date.toString('yyyy-MM-dd')}, Стать: {gender}")
            
            # Викликаємо метод оновлення розрахунків через parent dialog
            # parent() може бути QTabWidget, тому шукаємо EditClientDialog
            parent_dialog = self.parent()
            while parent_dialog and not hasattr(parent_dialog, '_trigger_calculations_update'):
                parent_dialog = parent_dialog.parent()
            
            if parent_dialog and hasattr(parent_dialog, '_trigger_calculations_update'):
                print("📊 Запускаю автоматичні розрахунки через EditClientDialog...")
                parent_dialog._trigger_calculations_update()
            else:
                print("⚠️ EditClientDialog не знайдено!")
        else:
            print(f"❌ Недостатньо даних для розрахунків. Дата: {birth_date.toString('yyyy-MM-dd')}, Стать: {gender}, Валідна дата: {is_valid_date}")
    
    def set_default_empty_values(self):
        """Встановлює всі поля пустими при створенні нового клієнта"""
        # Очищаємо всі текстові поля
        self.surname_edit.clear()
        self.first_name_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.spare_phone_edit.clear()
        self.occupation_edit.clear()
        self.address_edit.clear()
        
        # Встановлюємо дефолтні значення для комбобоксу та дати
        self.gender_combo.setCurrentIndex(0)  # "Оберіть стать"
        
        # ВАЖЛИВО: Встановлюємо дату народження пустою (мінімальна дата)
        self.birth_date_edit.setDate(QDate(1900, 1, 1))  # Мінімальна дата замість поточної
        
        print("🆕 Всі поля очищені для нового клієнта")
