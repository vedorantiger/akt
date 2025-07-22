# ui/dialogs/edit_client/physical_tab.py
"""Вкладка фізичних параметрів клієнта з автоматичними розрахунками"""
import math
from datetime import datetime, date
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QScrollArea, QLabel, QFrame)
from qfluentwidgets import LineEdit, ComboBox, DateEdit, SpinBox, DoubleSpinBox
from utils.calculations import FitnessCalculator


class PhysicalTab(QWidget):
    """Вкладка фізичних параметрів клієнта з автоматичними розрахунками"""
    
    # Сигнали для синхронізації даних між вкладками
    weight_changed = Signal(float)
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data or {}
        self.parent_dialog = parent  # Для отримання даних з інших вкладок
        self._init_ui()
        self._load_data()
        self._setup_calculations()
    
    def _init_ui(self):
        """Створює інтерфейс вкладки"""
        # Прокрутка для великої кількості полів
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
        
        # ===== ОСНОВНІ ПАРАМЕТРИ =====
        basic_group = QGroupBox("📏 Основні параметри")
        basic_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(basic_group)
        
        basic_form = QFormLayout(basic_group)
        basic_form.setSpacing(15)
        basic_form.setContentsMargins(20, 25, 20, 20)
        
        # Зріст
        self.height_spin = SpinBox()
        self.height_spin.setRange(0, 250)
        self.height_spin.setSuffix(" см")
        self.height_spin.setValue(0)  # ПУСТЕ поле - користувач сам введе
        self.height_spin.setMinimumHeight(40)
        self.height_spin.valueChanged.connect(self._update_calculations)
        basic_form.addRow("📐 Зріст:", self.height_spin)
        
        # Вага
        self.weight_spin = DoubleSpinBox()
        self.weight_spin.setRange(0.0, 300.0)
        self.weight_spin.setDecimals(1)
        self.weight_spin.setSuffix(" кг")
        self.weight_spin.setValue(0.0)  # ПУСТЕ поле - користувач сам введе
        self.weight_spin.setMinimumHeight(40)
        self.weight_spin.valueChanged.connect(self._on_weight_changed)
        self.weight_spin.valueChanged.connect(self._update_calculations)
        basic_form.addRow("⚖️ Вага:", self.weight_spin)
        
        # ===== СЕРЦЕВО-СУДИННІ ПОКАЗНИКИ =====
        cardio_group = QGroupBox("❤️ Серцево-судинні показники")
        cardio_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(cardio_group)
        
        cardio_form = QFormLayout(cardio_group)
        cardio_form.setSpacing(15)
        cardio_form.setContentsMargins(20, 25, 20, 20)
        
        # Артеріальний тиск (верхній/нижній)
        pressure_layout = QHBoxLayout()
        pressure_layout.setSpacing(10)
        
        # Верхній тиск
        upper_layout = QVBoxLayout()
        upper_label = QLabel("Верхній")
        upper_label.setStyleSheet("font-weight: 600; color: #374151;")
        upper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bp_systolic_spin = SpinBox()
        self.bp_systolic_spin.setRange(0, 200)
        self.bp_systolic_spin.setValue(0)  # ПУСТЕ поле - користувач сам введе
        self.bp_systolic_spin.setSuffix(" мм.рт.ст")
        self.bp_systolic_spin.setMinimumHeight(40)
        self.bp_systolic_spin.setFixedWidth(150)
        self.bp_systolic_spin.valueChanged.connect(self._update_calculations)
        upper_layout.addWidget(upper_label)
        upper_layout.addWidget(self.bp_systolic_spin)
        
        # Роздільник
        separator = QLabel("/")
        separator.setStyleSheet("font-size: 24px; font-weight: bold; color: #6B7280;")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setFixedWidth(20)
        
        # Нижній тиск
        lower_layout = QVBoxLayout()
        lower_label = QLabel("Нижній")
        lower_label.setStyleSheet("font-weight: 600; color: #374151;")
        lower_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bp_diastolic_spin = SpinBox()
        self.bp_diastolic_spin.setRange(0, 150)
        self.bp_diastolic_spin.setValue(0)  # ПУСТЕ поле - користувач сам введе
        self.bp_diastolic_spin.setSuffix(" мм.рт.ст")
        self.bp_diastolic_spin.setMinimumHeight(40)
        self.bp_diastolic_spin.setFixedWidth(150)
        self.bp_diastolic_spin.valueChanged.connect(self._update_calculations)
        lower_layout.addWidget(lower_label)
        lower_layout.addWidget(self.bp_diastolic_spin)
        
        pressure_layout.addLayout(upper_layout)
        pressure_layout.addWidget(separator)
        pressure_layout.addLayout(lower_layout)
        pressure_layout.addStretch()
        
        cardio_form.addRow("🩺 Артеріальний тиск:", pressure_layout)
        
        # ЧСС у спокої
        self.heart_rate_spin = SpinBox()
        self.heart_rate_spin.setRange(0, 200)
        self.heart_rate_spin.setSuffix(" уд/хв")
        self.heart_rate_spin.setValue(0)  # ПУСТЕ поле - користувач сам введе
        self.heart_rate_spin.setMinimumHeight(40)
        self.heart_rate_spin.valueChanged.connect(self._update_calculations)
        cardio_form.addRow("💓 ЧСС у спокої:", self.heart_rate_spin)
        
        # ===== МЕДИЧНІ ДАНІ =====
        medical_group = QGroupBox("🏥 Медичні дані")
        medical_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(medical_group)
        
        medical_form = QFormLayout(medical_group)
        medical_form.setSpacing(15)
        medical_form.setContentsMargins(20, 25, 20, 20)
        
        # Дата медогляду
        self.medical_exam_date_edit = DateEdit()
        self.medical_exam_date_edit.setDate(QDate.currentDate())
        self.medical_exam_date_edit.setMinimumHeight(40)
        medical_form.addRow("📅 Дата медогляду:", self.medical_exam_date_edit)
        
        # Медичний дозвіл
        self.medical_clearance_combo = ComboBox()
        self.medical_clearance_combo.addItems([
            "Не потрібен",
            "Потрібен", 
            "Є дозвіл"
        ])
        self.medical_clearance_combo.setMinimumHeight(40)
        medical_form.addRow("📋 Медичний дозвіл:", self.medical_clearance_combo)
        
        # Споживання води
        self.water_intake_spin = DoubleSpinBox()
        self.water_intake_spin.setRange(0.5, 10.0)
        self.water_intake_spin.setDecimals(1)
        self.water_intake_spin.setSuffix(" л/день")
        self.water_intake_spin.setValue(2.0)
        self.water_intake_spin.setMinimumHeight(40)
        medical_form.addRow("💧 Споживання води:", self.water_intake_spin)
        
        # Цикл місячних (тільки для жінок)
        self.menstrual_cycle_edit = LineEdit()
        self.menstrual_cycle_edit.setPlaceholderText("Інформація про менструальний цикл")
        self.menstrual_cycle_edit.setMinimumHeight(40)
        self.menstrual_row = medical_form.addRow("🌸 Цикл місячних:", self.menstrual_cycle_edit)
        
        # ===== РОЗРАХУНКОВІ ПОКАЗНИКИ =====
        calculations_group = QGroupBox("🧮 Розрахункові показники (автоматично)")
        calculations_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(calculations_group)
        
        calc_layout = QVBoxLayout(calculations_group)
        calc_layout.setContentsMargins(20, 25, 20, 20)
        calc_layout.setSpacing(15)
        
        # Контейнер для всіх розрахунків
        self.calculations_container = QWidget()
        self.calculations_layout = QVBoxLayout(self.calculations_container)
        self.calculations_layout.setSpacing(10)
        calc_layout.addWidget(self.calculations_container)
        
        # Початково створюємо пусті лейбли для розрахунків
        self._create_calculation_displays()
        
    def _create_calculation_displays(self):
        """Створює елементи для відображення розрахунків"""
        # ІМТ
        self.bmi_display = self._create_calculation_card("📊 ІМТ (Індекс Маси Тіла)", "Введіть зріст та вагу")
        
        # Відсоток жиру
        self.body_fat_display = self._create_calculation_card("🥩 Відсоток жиру в організмі", "Введіть базові дані")
        
        # М'язова маса
        self.muscle_mass_display = self._create_calculation_card("💪 М'язова маса", "Введіть базові дані")
        
        # Тип тілобудови
        self.body_type_display = self._create_calculation_card("🏗️ Тип тілобудови", "Введіть базові дані")
        
        # BMR
        self.bmr_display = self._create_calculation_card("🔥 Базальний метаболізм (BMR)", "Введіть базові дані")
        
        # Денна потреба в калоріях
        self.calories_display = self._create_calculation_card("🍽️ Денна потреба в калоріях", "Введіть базові дані")
        self.daily_calories_display = self.calories_display  # Псевдонім для сумісності
        
        # Ідеальна вага
        self.ideal_weight_display = self._create_calculation_card("⚖️ Ідеальна вага", "Введіть зріст та стать")
        
        # Норма води
        self.water_display = self._create_calculation_card("💧 Денна норма води", "Введіть вагу")
        
        # ЧСС статус
        self.hr_status_display = self._create_calculation_card("💓 Статус ЧСС у спокої", "Введіть ЧСС")
        
        # Пульсові зони
        self.hr_zones_display = self._create_calculation_card("🎯 Пульсові зони тренувань", "Введіть вік")
    
    def _create_calculation_card(self, title, default_text):
        """Створює картку для відображення розрахунку"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title_label)
        
        # Значення
        value_label = QLabel(default_text)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #6B7280;
                background: transparent;
                border: none;
                padding: 4px 0px;
            }
        """)
        value_label.setWordWrap(True)
        layout.addWidget(value_label)
        
        self.calculations_layout.addWidget(card)
        return value_label
    
    def _on_weight_changed(self, value):
        """Обробляє зміну ваги та сигналізує іншим вкладкам"""
        self.weight_changed.emit(value)
    
    def _setup_calculations(self):
        """Налаштовує автоматичні розрахунки при зміні полів"""
        # Підключаємо оновлення розрахунків до зміни значень основних полів
        self.height_spin.valueChanged.connect(self._update_calculations)
        self.weight_spin.valueChanged.connect(self._update_calculations)
        self.weight_spin.valueChanged.connect(self._on_weight_changed)
        self.heart_rate_spin.valueChanged.connect(self._update_calculations)
        
        # Виконуємо початковий розрахунок
        self._update_calculations()
    
    def _update_calculations(self):
        """Оновлює всі розрахунки автоматично в режимі реального часу"""
        try:
            print("🔥 Починаю оновлення розрахунків...")
            
            # Отримуємо базові дані
            height_cm = self.height_spin.value() if self.height_spin.value() > 0 else None
            weight_kg = self.weight_spin.value() if self.weight_spin.value() > 0 else None
            hr_rest = self.heart_rate_spin.value() if self.heart_rate_spin.value() > 0 else None
            
            # Отримуємо дані з інших вкладок
            age = self._get_age()
            gender = self._get_gender()
            activity_level = self._get_activity_level()
            
            print(f"📊 Дані для розрахунків: зріст={height_cm}, вага={weight_kg}, вік={age}, стать={gender}, пульс={hr_rest}")
            
            # Показуємо/приховуємо поле циклу місячних
            self._toggle_menstrual_field(gender)
            
            # ===== БЕЗПЕЧНІ РОЗРАХУНКИ З НАЯВНИМИ ДАНИМИ =====
            
            # 1. Пульсові зони (потрібен тільки вік)
            if age and age > 10:
                self._calculate_hr_zones_simple(age)
                print("✅ Розраховано пульсові зони")
            else:
                self.hr_zones_display.setText("Введіть дату народження для розрахунку пульсових зон")
            
            # 2. Статус ЧСС (потрібен тільки пульс)
            if hr_rest and hr_rest > 30:
                self._calculate_hr_status_simple(hr_rest)
                print("✅ Розраховано статус ЧСС")
            else:
                self.hr_status_display.setText("Введіть ЧСС у спокої")
            
            # 3. ІМТ (потрібні зріст та вага)
            if height_cm and weight_kg and height_cm > 100 and weight_kg > 20:
                self._calculate_bmi_simple(height_cm, weight_kg)
                print("✅ Розраховано ІМТ")
            else:
                self.bmi_display.setText("Введіть зріст та вагу для розрахунку ІМТ")
            
            # 4. BMR (потрібні зріст, вага, вік, стать)
            if height_cm and weight_kg and age and gender and height_cm > 100 and weight_kg > 20 and age > 10:
                self._calculate_bmr_simple(height_cm, weight_kg, age, gender)
                print("✅ Розраховано BMR")
            else:
                self.bmr_display.setText("Введіть зріст, вагу, вік та стать для розрахунку BMR")
            
            # 5. Норма води (потрібна тільки вага)
            if weight_kg and weight_kg > 20:
                self._calculate_water_simple(weight_kg)
                print("✅ Розраховано норму води")
            else:
                self.water_display.setText("Введіть вагу для розрахунку норми води")
                
            # 6. Інші розрахунки поки залишаємо як заглушки
            self.body_fat_display.setText("Введіть всі базові дані")
            self.muscle_mass_display.setText("Введіть всі базові дані") 
            self.body_type_display.setText("Введіть всі базові дані")
            self.ideal_weight_display.setText("Введіть зріст та стать")
            self.daily_calories_display.setText("Введіть всі базові дані")
            
            print("✅ Оновлення розрахунків завершено")
            
        except Exception as e:
            print(f"❌ Помилка розрахунків: {e}")
            # Очищаємо відображення при помилках
            self._clear_calculations_display()
            
            # 4. BMR та калорії (потрібні зріст, вага, вік, стать)
            if height_cm and weight_kg and age and gender:
                self._calculate_bmr_simple(height_cm, weight_kg, age, gender, activity_level)
                print("✅ Розраховано BMR та калорії")
            else:
                self.bmr_display.setText("Введіть зріст, вагу, вік та стать")
                self.daily_calories_display.setText("Введіть зріст, вагу, вік та стать")
            
            # 5. Відсоток жиру (потрібні зріст, вага, вік, стать)  
            if height_cm and weight_kg and age and gender:
                self._calculate_body_fat_simple(height_cm, weight_kg, age, gender)
                print("✅ Розраховано відсоток жиру")
            else:
                self.body_fat_display.setText("Введіть зріст, вагу, вік та стать")
            
            # 6. М'язова маса (потрібні зріст, вага, вік, стать)
            if height_cm and weight_kg and age and gender:
                self._calculate_muscle_mass_simple(height_cm, weight_kg, age, gender)
                print("✅ Розраховано м'язову масу")
            else:
                self.muscle_mass_display.setText("Введіть зріст, вагу, вік та стать")
            
            # 7. Тип тілобудови (потрібні зріст, вага)
            if height_cm and weight_kg:
                self._calculate_body_type_simple(height_cm, weight_kg, gender)
                print("✅ Розраховано тип тілобудови")
            else:
                self.body_type_display.setText("Введіть зріст та вагу")
            
            # 8. Ідеальна вага (потрібні зріст, стать)
            if height_cm and gender:
                self._calculate_ideal_weight_simple(height_cm, gender)
                print("✅ Розраховано ідеальну вагу")
            else:
                self.ideal_weight_display.setText("Введіть зріст та стать")
            
            # 9. Норма води (потрібна вага)
            if weight_kg:
                self._calculate_water_intake_simple(weight_kg)
                print("✅ Розраховано норму води")
            else:
                self.water_display.setText("Введіть вагу для розрахунку норми води")
            
            print("✅ Оновлення розрахунків завершено")
            
        except Exception as e:
            print(f"❌ Помилка розрахунків: {e}")
            # Логуємо помилку, але не виводимо в консоль
            if hasattr(self, 'parent_dialog') and hasattr(self.parent_dialog, 'logger'):
                self.parent_dialog.logger.error(f"Помилка розрахунків: {e}")
            # Очищаємо відображення при помилках
            self._clear_calculations_display()
            self._clear_calculations_display()
    
    def _get_age(self):
        """Отримує вік з вкладки основних даних"""
        try:
            if hasattr(self.parent_dialog, 'basic_tab'):
                birth_date = self.parent_dialog.basic_tab.birth_date_edit.date().toPython()
                
                # Перевіряємо чи це реальна дата народження (не мінімальна)
                if birth_date.year <= 1950:
                    return None
                
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                # Перевіряємо чи вік реальний
                if age < 5 or age > 120:
                    return None
                
                return age
        except Exception as e:
            print(f"Помилка розрахунку віку: {e}")
        return None
    
    def _get_gender(self):
        """Отримує стать з вкладки основних даних"""
        try:
            if hasattr(self.parent_dialog, 'basic_tab'):
                gender_text = self.parent_dialog.basic_tab.gender_combo.currentText()
                if "Чоловік" in gender_text:
                    return "male"
                elif "Жінка" in gender_text:
                    return "female"
        except:
            pass
        return None
    
    def _get_activity_level(self):
        """Отримує рівень активності з вкладки способу життя"""
        try:
            if hasattr(self.parent_dialog, 'lifestyle_tab'):
                activity_text = self.parent_dialog.lifestyle_tab.activity_level_combo.currentText()
                return activity_text
        except:
            pass
        return None
    
    def _toggle_menstrual_field(self, gender):
        """Показує/приховує поле циклу місячних"""
        try:
            if hasattr(self, 'menstrual_cycle_edit') and hasattr(self, 'menstrual_row'):
                if gender == "female":
                    self.menstrual_cycle_edit.setVisible(True)
                    if self.menstrual_row and len(self.menstrual_row) > 0:
                        self.menstrual_row[0].setVisible(True)  # Лейбл
                else:
                    self.menstrual_cycle_edit.setVisible(False)
                    if self.menstrual_row and len(self.menstrual_row) > 0:
                        self.menstrual_row[0].setVisible(False)  # Лейбл
        except Exception as e:
            print(f"⚠️ Помилка при роботі з полем циклу: {e}")
    
    # ===== СПРОЩЕНІ МЕТОДИ РОЗРАХУНКІВ =====
    
    def _calculate_hr_zones_simple(self, age):
        """Спрощений розрахунок пульсових зон"""
        max_hr = 220 - age
        
        zones_html = f"""
        <div style='background: #F8F9FA; padding: 12px; border-radius: 8px;'>
            <div style='font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 8px;'>
                🎯 Пульсові зони (макс. {max_hr} уд/хв):
            </div>
            <div style='margin: 4px 0; padding: 6px; background: #10B98120; border-left: 4px solid #10B981; border-radius: 4px;'>
                <span style='color: #10B981; font-weight: 600;'>😌 ВІДНОВЛЕННЯ</span>
                <span style='color: #6B7280; margin-left: 8px;'>{int(max_hr * 0.5)}-{int(max_hr * 0.6)} уд/хв (50-60%)</span>
            </div>
            <div style='margin: 4px 0; padding: 6px; background: #F59E0B20; border-left: 4px solid #F59E0B; border-radius: 4px;'>
                <span style='color: #F59E0B; font-weight: 600;'>🔥 ЖИРОСПАЛЮВАННЯ</span>
                <span style='color: #6B7280; margin-left: 8px;'>{int(max_hr * 0.6)}-{int(max_hr * 0.7)} уд/хв (60-70%)</span>
            </div>
            <div style='margin: 4px 0; padding: 6px; background: #3B82F620; border-left: 4px solid #3B82F6; border-radius: 4px;'>
                <span style='color: #3B82F6; font-weight: 600;'>🏃 АЕРОБНА</span>
                <span style='color: #6B7280; margin-left: 8px;'>{int(max_hr * 0.7)}-{int(max_hr * 0.8)} уд/хв (70-80%)</span>
            </div>
            <div style='margin: 4px 0; padding: 6px; background: #8B5CF620; border-left: 4px solid #8B5CF6; border-radius: 4px;'>
                <span style='color: #8B5CF6; font-weight: 600;'>⚡ АНАЕРОБНА</span>
                <span style='color: #6B7280; margin-left: 8px;'>{int(max_hr * 0.8)}-{int(max_hr * 0.9)} уд/хв (80-90%)</span>
            </div>
            <div style='margin: 4px 0; padding: 6px; background: #EF444420; border-left: 4px solid #EF4444; border-radius: 4px;'>
                <span style='color: #EF4444; font-weight: 600;'>🔥 МАКСИМАЛЬНА</span>
                <span style='color: #6B7280; margin-left: 8px;'>{int(max_hr * 0.9)}-{max_hr} уд/хв (90-100%)</span>
            </div>
        </div>
        """
        
        self.hr_zones_display.setText(zones_html)
        self.hr_zones_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_hr_status_simple(self, hr_rest, age):
        """Спрощений розрахунок статусу ЧСС"""
        if hr_rest < 50:
            status = "❄️ Занадто низький"
            description = "Може вимагати консультації лікаря"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        elif hr_rest < 60:
            status = "📉 Низький"
            description = "Часто у добре тренованих людей"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        elif hr_rest < 70:
            status = "✅ Оптимальний"
            description = "Найкращі показники для здоров'я"
            color = "#10B981"
            bg_color = "#D1FAE5"
        elif hr_rest < 80:
            status = "👍 Нормальний"
            description = "Типові показники"
            color = "#3B82F6"
            bg_color = "#DBEAFE"
        elif hr_rest < 90:
            status = "📈 Підвищений"
            description = "Можливо, потрібно більше активності"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        else:
            status = "🔥 Високий"
            description = "Рекомендована консультація лікаря"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ЧСС: {hr_rest} уд/хв</div>
            <div style='font-size: 14px; margin-top: 4px;'>{status}</div>
            <div style='font-size: 12px; color: #6B7280; margin-top: 4px;'>{description}</div>
        </div>
        """
        
        self.hr_status_display.setText(result_text)
        self.hr_status_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_bmi_simple(self, height_cm, weight_kg):
        """Спрощений розрахунок ІМТ"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Недостатня вага"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        elif 18.5 <= bmi < 25:
            category = "Нормальна вага"
            color = "#10B981"
            bg_color = "#D1FAE5"
        elif 25 <= bmi < 30:
            category = "Надмірна вага"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        else:
            category = "Ожиріння"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ІМТ: {bmi:.1f}</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.bmi_display.setText(result_text)
        self.bmi_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_bmr_simple(self, height_cm, weight_kg, age, gender, activity_level=None):
        """Спрощений розрахунок BMR та калорій"""
        # Формула Міффліна-Сан Жеора
        if gender == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Коефіцієнт активності
        multiplier = 1.55  # За замовчуванням помірна активність
        if activity_level and "Мінімальна" in str(activity_level):
            multiplier = 1.2
        elif activity_level and "Легка" in str(activity_level):
            multiplier = 1.375
        elif activity_level and "Висока" in str(activity_level):
            multiplier = 1.725
        elif activity_level and "Дуже висока" in str(activity_level):
            multiplier = 1.9
        
        maintenance = int(bmr * multiplier)
        cutting = int(maintenance * 0.8)
        bulking = int(maintenance * 1.2)
        
        # BMR
        bmr_text = f"""
        <div style='background: #FEF3C7; padding: 8px; border-radius: 6px; color: #D97706; font-weight: 600;'>
            <div style='font-size: 16px;'>BMR: {int(bmr)} ккал/день</div>
            <div style='font-size: 12px; margin-top: 4px; font-weight: normal;'>Мінімальна енергія для життєдіяльності</div>
        </div>
        """
        self.bmr_display.setText(bmr_text)
        self.bmr_display.setStyleSheet("QLabel { background: transparent; border: none; }")
        
        # Калорії
        calories_text = f"""
        <div style='background: #ECFDF5; padding: 12px; border-radius: 8px; color: #059669; font-weight: 600;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>Денні калорії:</div>
            <div style='font-size: 14px; margin: 4px 0;'>🎯 Підтримка: {maintenance} ккал</div>
            <div style='font-size: 14px; margin: 4px 0;'>📉 Схуднення: {cutting} ккал</div>
            <div style='font-size: 14px; margin: 4px 0;'>📈 Набір маси: {bulking} ккал</div>
        </div>
        """
        self.daily_calories_display.setText(calories_text)
        self.daily_calories_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_body_fat_simple(self, height_cm, weight_kg, age, gender):
        """Спрощений розрахунок відсотка жиру"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Формула Deurenberg
        if gender == "male":
            body_fat = 1.20 * bmi + 0.23 * age - 16.2
        else:  # female
            body_fat = 1.20 * bmi + 0.23 * age - 5.4
        
        result_text = f"""
        <div style='background: #DBEAFE; padding: 8px; border-radius: 6px; color: #3B82F6; font-weight: 600;'>
            <div style='font-size: 16px;'>Жир у тілі: {body_fat:.1f}%</div>
            <div style='font-size: 12px; margin-top: 4px; color: #6B7280; font-weight: normal;'>За формулою Deurenberg</div>
        </div>
        """
        
        self.body_fat_display.setText(result_text)
        self.body_fat_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_muscle_mass_simple(self, height_cm, weight_kg, age, gender):
        """Спрощений розрахунок м'язової маси"""
        # Формула Janssen
        if gender == "male":
            muscle_mass = (0.407 * weight_kg) + (0.267 * height_cm) - (0.049 * age) + 5.09
        else:  # female
            muscle_mass = (0.252 * weight_kg) + (0.473 * height_cm) - (0.048 * age) + 2.83
        
        muscle_percentage = (muscle_mass / weight_kg) * 100
        
        result_text = f"""
        <div style='background: #D1FAE5; padding: 8px; border-radius: 6px; color: #10B981; font-weight: 600;'>
            <div style='font-size: 16px;'>М'язова маса: {muscle_mass:.1f} кг</div>
            <div style='font-size: 14px; margin-top: 4px;'>{muscle_percentage:.1f}% від ваги</div>
        </div>
        """
        
        self.muscle_mass_display.setText(result_text)
        self.muscle_mass_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_body_type_simple(self, height_cm, weight_kg, gender):
        """Спрощений розрахунок типу тілобудови"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 20:
            body_type = "Ектоморф"
            description = "Тонке, худе тіло з швидким метаболізмом"
            color = "#3B82F6"
            bg_color = "#DBEAFE"
        elif bmi < 25:
            body_type = "Мезоморф"
            description = "Атлетичне, мускулисте тіло"
            color = "#10B981"
            bg_color = "#D1FAE5"
        else:
            body_type = "Ендоморф"
            description = "Широка кісткова структура"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 12px; border-radius: 8px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>Тип: {body_type}</div>
            <div style='font-size: 12px; color: #6B7280; line-height: 1.4;'>{description}</div>
        </div>
        """
        
        self.body_type_display.setText(result_text)
        self.body_type_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_ideal_weight_simple(self, height_cm, gender):
        """Спрощений розрахунок ідеальної ваги"""
        if gender == "male":
            ideal_weight = (height_cm - 100) * 0.9
        else:  # female
            ideal_weight = (height_cm - 100) * 0.85
        
        result_text = f"""
        <div style='background: #F3E8FF; padding: 8px; border-radius: 6px; color: #8B5CF6; font-weight: 600;'>
            <div style='font-size: 16px;'>Ідеальна вага: {ideal_weight:.1f} кг</div>
            <div style='font-size: 12px; margin-top: 4px; color: #6B7280; font-weight: normal;'>За спрощеною формулою</div>
        </div>
        """
        
        self.ideal_weight_display.setText(result_text)
        self.ideal_weight_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_water_intake_simple(self, weight_kg):
        """Спрощений розрахунок норми води"""
        water_intake = weight_kg * 0.035  # 35 мл на кг ваги
        
        result_text = f"""
        <div style='background: #E0F2FE; padding: 8px; border-radius: 6px; color: #0891B2; font-weight: 600;'>
            <div style='font-size: 16px;'>Норма води: {water_intake:.1f} л/день</div>
            <div style='font-size: 12px; margin-top: 4px; color: #6B7280; font-weight: normal;'>35 мл на кг ваги</div>
        </div>
        """
        
        self.water_display.setText(result_text)
        self.water_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    # ===== КІНЕЦЬ СПРОЩЕНИХ МЕТОДІВ =====
    
    def _calculate_bmi(self, height_cm, weight_kg):
        """Розрахунок ІМТ"""
        if height_cm <= 0 or weight_kg <= 0:
            self.bmi_display.setText("Введіть зріст та вагу")
            return
        
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Визначення категорії та кольору
        if bmi < 18.5:
            category = "Недостатня вага"
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        elif 18.5 <= bmi < 25:
            category = "Норма"
            color = "#10B981"  # Зелений
            bg_color = "#D1FAE5"
        elif 25 <= bmi < 30:
            category = "Надлишкова вага"
            color = "#F59E0B"  # Помаранчевий
            bg_color = "#FEF3C7"
        else:
            category = "Ожиріння"
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ІМТ: {bmi:.1f}</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.bmi_display.setText(result_text)
        self.bmi_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_body_fat(self, height_cm, weight_kg, age, gender):
        """Розрахунок відсотка жиру за формулою Deurenberg"""
        if not all([height_cm, weight_kg, age, gender]):
            self.body_fat_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Формула Deurenberg
        if gender == "male":
            body_fat = 1.20 * bmi + 0.23 * age - 16.2
        else:  # female
            body_fat = 1.20 * bmi + 0.23 * age - 5.4
        
        # Визначення категорії
        if gender == "male":
            if body_fat < 6:
                category = "Дуже низький"
                color = "#3B82F6"  # Блакитний
                bg_color = "#DBEAFE"
            elif body_fat < 14:
                category = "Низький"
                color = "#06B6D4"  # Бірюзовий
                bg_color = "#CFFAFE"
            elif body_fat < 25:
                category = "Нормальний"
                color = "#10B981"  # Зелений
                bg_color = "#D1FAE5"
            else:
                category = "Високий"
                color = "#EF4444"  # Червоний
                bg_color = "#FEE2E2"
        else:  # female
            if body_fat < 16:
                category = "Дуже низький"
                color = "#3B82F6"  # Блакитний
                bg_color = "#DBEAFE"
            elif body_fat < 20:
                category = "Низький"
                color = "#06B6D4"  # Бірюзовий
                bg_color = "#CFFAFE"
            elif body_fat < 30:
                category = "Нормальний"
                color = "#10B981"  # Зелений
                bg_color = "#D1FAE5"
            else:
                category = "Високий"
                color = "#EF4444"  # Червоний
                bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>Жир: {body_fat:.1f}%</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.body_fat_display.setText(result_text)
        self.body_fat_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_muscle_mass(self, height_cm, weight_kg, age, gender):
        """Розрахунок м'язової маси за формулою Janssen"""
        if not all([height_cm, weight_kg, age, gender]):
            self.muscle_mass_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        height_m = height_cm / 100
        
        # Формула Janssen для скелетної м'язової маси
        if gender == "male":
            muscle_mass = (0.407 * weight_kg) + (0.267 * height_cm) - (0.049 * age) + 5.09
        else:  # female
            muscle_mass = (0.252 * weight_kg) + (0.473 * height_cm) - (0.048 * age) + 2.83
        
        muscle_percentage = (muscle_mass / weight_kg) * 100
        
        # Визначення категорії
        if gender == "male":
            if muscle_percentage < 37:
                category = "Низький"
                color = "#EF4444"  # Червоний
                bg_color = "#FEE2E2"
            elif muscle_percentage < 45:
                category = "Нормальний"
                color = "#10B981"  # Зелений
                bg_color = "#D1FAE5"
            else:
                category = "Високий"
                color = "#3B82F6"  # Блакитний
                bg_color = "#DBEAFE"
        else:  # female
            if muscle_percentage < 31:
                category = "Низький"
                color = "#EF4444"  # Червоний
                bg_color = "#FEE2E2"
            elif muscle_percentage < 36:
                category = "Нормальний"
                color = "#10B981"  # Зелений
                bg_color = "#D1FAE5"
            else:
                category = "Високий"
                color = "#3B82F6"  # Блакитний
                bg_color = "#DBEAFE"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>М'язи: {muscle_mass:.1f} кг ({muscle_percentage:.1f}%)</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.muscle_mass_display.setText(result_text)
        self.muscle_mass_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_body_type(self, height_cm, weight_kg, age, gender):
        """Визначення типу тілобудови (соматотипу)"""
        if not all([height_cm, weight_kg, gender]):
            self.body_type_display.setText("Введіть зріст, вагу та стать")
            return
        
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Спрощений алгоритм визначення соматотипу на основі ІМТ
        if bmi < 20:
            body_type = "Ектоморф"
            description = "Тонке, худе тіло з вузькими кістками та низьким рівнем жиру. Метаболізм швидкий, важко набирати вагу."
            color = "#3B82F6"  # Блакитний
            bg_color = "#DBEAFE"
        elif bmi < 25:
            body_type = "Мезоморф"
            description = "Атлетичне, мускулисте тіло з широкими плечима. Метаболізм середній, легко нарощують м'язи."
            color = "#10B981"  # Зелений
            bg_color = "#D1FAE5"
        else:
            body_type = "Ендоморф"
            description = "Широка кісткова структура, схильність до набору жиру. Метаболізм повільний, легко набирають вагу."
            color = "#F59E0B"  # Помаранчевий
            bg_color = "#FEF3C7"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>{body_type}</div>
            <div style='font-size: 12px; margin-top: 4px; color: #374151; font-weight: normal;'>{description}</div>
        </div>
        """
        
        self.body_type_display.setText(result_text)
        self.body_type_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_bmr(self, height_cm, weight_kg, age, gender):
        """Розрахунок базального метаболізму за формулою Міффліна-Сан Жеора"""
        if not all([height_cm, weight_kg, age, gender]):
            self.bmr_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        # Формула Міффліна-Сан Жеора
        if gender == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        result_text = f"""
        <div style='background: #F3F4F6; padding: 8px; border-radius: 6px; color: #374151; font-weight: 600;'>
            <div style='font-size: 16px;'>BMR: {bmr:.0f} ккал/день</div>
            <div style='font-size: 12px; margin-top: 4px; font-weight: normal;'>Мінімальна енергія для життєдіяльності</div>
        </div>
        """
        
        self.bmr_display.setText(result_text)
        self.bmr_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_daily_calories(self, height_cm, weight_kg, age, gender, activity_level):
        """Розрахунок денної потреби в калоріях"""
        if not all([height_cm, weight_kg, age, gender]):
            self.calories_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        # Розрахунок BMR
        if gender == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Коефіцієнти активності
        activity_multipliers = {
            "Мінімальна активність": 1.2,
            "Легка активність": 1.375,
            "Помірна активність": 1.55,
            "Висока активність": 1.725,
            "Дуже висока активність": 1.9
        }
        
        multiplier = 1.55  # За замовчуванням помірна активність
        if activity_level and activity_level in activity_multipliers:
            multiplier = activity_multipliers[activity_level]
        
        maintenance_calories = bmr * multiplier
        cutting_calories = maintenance_calories * 0.8  # -20% для схуднення
        bulking_calories = maintenance_calories * 1.2   # +20% для набору маси
        
        result_text = f"""
        <div style='background: #F3F4F6; padding: 8px; border-radius: 6px; color: #374151; font-weight: 600;'>
            <div style='font-size: 14px;'>🎯 Підтримка: {maintenance_calories:.0f} ккал/день</div>
            <div style='font-size: 14px; margin-top: 2px;'>📉 Схуднення: {cutting_calories:.0f} ккал/день</div>
            <div style='font-size: 14px; margin-top: 2px;'>📈 Набір маси: {bulking_calories:.0f} ккал/день</div>
        </div>
        """
        
        self.calories_display.setText(result_text)
        self.calories_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_hr_status(self, hr_rest, age):
        """Визначення статусу ЧСС у спокої"""
        if not hr_rest:
            self.hr_status_display.setText("Введіть ЧСС у спокої")
            return
        
        # Визначення статусу ЧСС
        if hr_rest < 50:
            status = "❄️ Занадто низький"
            description = "Може вимагати консультації лікаря"
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        elif hr_rest < 60:
            status = "📉 Низький"
            description = "Часто у добре тренованих людей"
            color = "#F59E0B"  # Помаранчевий
            bg_color = "#FEF3C7"
        elif hr_rest < 70:
            status = "✅ Оптимальний"
            description = "Найкращі показники для здоров'я"
            color = "#10B981"  # Зелений
            bg_color = "#D1FAE5"
        elif hr_rest < 80:
            status = "👍 Нормальний"
            description = "Типові показники"
            color = "#3B82F6"  # Блакитний
            bg_color = "#DBEAFE"
        elif hr_rest < 90:
            status = "📈 Підвищений"
            description = "Можливо, потрібно більше активності"
            color = "#F59E0B"  # Помаранчевий
            bg_color = "#FEF3C7"
        else:
            status = "🔥 Високий"
            description = "Рекомендована консультація лікаря"
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>{status}</div>
            <div style='font-size: 12px; margin-top: 4px; color: #374151; font-weight: normal;'>{description}</div>
        </div>
        """
        
        self.hr_status_display.setText(result_text)
        self.hr_status_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_hr_zones(self, age):
        """Розрахунок пульсових зон тренувань"""
        if not age:
            self.hr_zones_display.setText("Введіть дату народження для розрахунку віку")
            return
        
        max_hr = 220 - age
        
        # Зони тренувань (відсотки від максимального пульсу)
        recovery_min = int(max_hr * 0.5)
        recovery_max = int(max_hr * 0.6)
        
        fat_burn_min = int(max_hr * 0.6)
        fat_burn_max = int(max_hr * 0.7)
        
        aerobic_min = int(max_hr * 0.7)
        aerobic_max = int(max_hr * 0.8)
        
        anaerobic_min = int(max_hr * 0.8)
        anaerobic_max = int(max_hr * 0.9)
        
        max_min = int(max_hr * 0.9)
        max_max = max_hr
        
        result_text = f"""
        <div style='background: #F3F4F6; padding: 8px; border-radius: 6px; color: #374151; font-weight: 600;'>
            <div style='font-size: 14px; margin-bottom: 6px;'>🎯 Максимальний пульс: {max_hr} уд/хв</div>
            <div style='font-size: 12px; color: #10B981;'>😌 ВІДНОВЛЕННЯ: {recovery_min}-{recovery_max} уд/хв</div>
            <div style='font-size: 12px; color: #F59E0B;'>🔥 ЖИРОСПАЛЮВАННЯ: {fat_burn_min}-{fat_burn_max} уд/хв</div>
            <div style='font-size: 12px; color: #3B82F6;'>🏃 АЕРОБНА: {aerobic_min}-{aerobic_max} уд/хв</div>
            <div style='font-size: 12px; color: #8B5CF6;'>⚡ АНАЕРОБНА: {anaerobic_min}-{anaerobic_max} уд/хв</div>
            <div style='font-size: 12px; color: #EF4444;'>🔥 МАКСИМАЛЬНА: {max_min}-{max_max} уд/хв</div>
        </div>
        """
        
        self.hr_zones_display.setText(result_text)
        self.hr_zones_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    # ===== НОВІ МЕТОДИ ОНОВЛЕННЯ ВІДОБРАЖЕННЯ =====
    
    def _update_bmi_display(self, bmi, category):
        """Оновлює відображення ІМТ"""
        if not bmi:
            self.bmi_display.setText("Введіть зріст та вагу")
            return
        
        # Визначення кольору за категорією
        if "Недостатня" in category:
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        elif "Нормальна" in category:
            color = "#10B981"  # Зелений
            bg_color = "#D1FAE5"
        elif "Надмірна" in category:
            color = "#F59E0B"  # Помаранчевий
            bg_color = "#FEF3C7"
        else:  # Ожиріння
            color = "#EF4444"  # Червоний
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ІМТ: {bmi}</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.bmi_display.setText(result_text)
        self.bmi_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_body_fat_display(self, body_fat):
        """Оновлює відображення відсотка жиру"""
        if not body_fat:
            self.body_fat_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        result_text = f"""
        <div style='background: #DBEAFE; padding: 8px; border-radius: 6px; color: #3B82F6; font-weight: 600;'>
            <div style='font-size: 16px;'>Жир у тілі: {body_fat}%</div>
        </div>
        """
        
        self.body_fat_display.setText(result_text)
        self.body_fat_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_ideal_weight_display(self, ideal_weight):
        """Оновлює відображення ідеальної ваги"""
        if not ideal_weight:
            self.ideal_weight_display.setText("Введіть зріст та стать")
            return
        
        result_text = f"""
        <div style='background: #F3E8FF; padding: 8px; border-radius: 6px; color: #8B5CF6; font-weight: 600;'>
            <div style='font-size: 16px;'>Ідеальна вага: {ideal_weight} кг</div>
        </div>
        """
        
        if hasattr(self, 'ideal_weight_display'):
            self.ideal_weight_display.setText(result_text)
            self.ideal_weight_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_bmr_display(self, bmr):
        """Оновлює відображення базального метаболізму"""
        if not bmr:
            self.bmr_display.setText("Введіть зріст, вагу, вік та стать")
            return
        
        result_text = f"""
        <div style='background: #FEF3C7; padding: 8px; border-radius: 6px; color: #D97706; font-weight: 600;'>
            <div style='font-size: 16px;'>BMR: {int(bmr)} ккал/день</div>
        </div>
        """
        
        if hasattr(self, 'bmr_display'):
            self.bmr_display.setText(result_text)
            self.bmr_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_daily_calories_display(self, daily_calories_detailed):
        """Оновлює відображення денних калорій з деталями"""
        if not daily_calories_detailed:
            return
        
        maintenance = daily_calories_detailed.get('maintenance', 0)
        weight_loss = daily_calories_detailed.get('weight_loss', 0)
        weight_gain = daily_calories_detailed.get('weight_gain', 0)
        
        result_text = f"""
        <div style='background: #ECFDF5; padding: 12px; border-radius: 8px; color: #059669; font-weight: 600;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>Денні калорії:</div>
            <div style='font-size: 14px; margin: 4px 0;'>🎯 Підтримка: {maintenance} ккал</div>
            <div style='font-size: 14px; margin: 4px 0;'>📉 Схуднення: {weight_loss} ккал</div>
            <div style='font-size: 14px; margin: 4px 0;'>📈 Набір маси: {weight_gain} ккал</div>
        </div>
        """
        
        if hasattr(self, 'daily_calories_display'):
            self.daily_calories_display.setText(result_text)
            self.daily_calories_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_muscle_mass_display(self, muscle_mass_data):
        """Оновлює відображення м'язової маси"""
        if not muscle_mass_data:
            return
        
        mass_kg = muscle_mass_data.get('mass_kg', 0)
        percentage = muscle_mass_data.get('percentage', 0)
        category = muscle_mass_data.get('category', '')
        color = muscle_mass_data.get('color', '#6B7280')
        
        # Визначаємо колір фону
        bg_colors = {
            '#EF4444': '#FEE2E2',  # Червоний -> Світло-червоний
            '#10B981': '#D1FAE5',  # Зелений -> Світло-зелений
            '#3B82F6': '#DBEAFE'   # Блакитний -> Світло-блакитний
        }
        bg_color = bg_colors.get(color, '#F3F4F6')
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>М'язова маса: {mass_kg} кг</div>
            <div style='font-size: 14px; margin-top: 4px;'>{percentage}% - {category}</div>
        </div>
        """
        
        if hasattr(self, 'muscle_mass_display'):
            self.muscle_mass_display.setText(result_text)
            self.muscle_mass_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_body_type_display(self, body_type_data):
        """Оновлює відображення типу тілобудови"""
        if not body_type_data:
            return
        
        body_type = body_type_data.get('type', '')
        description = body_type_data.get('description', '')
        color = body_type_data.get('color', '#6B7280')
        
        # Визначаємо колір фону
        bg_colors = {
            '#EF4444': '#FEE2E2',  # Червоний -> Світло-червоний
            '#10B981': '#D1FAE5',  # Зелений -> Світло-зелений
            '#3B82F6': '#DBEAFE'   # Блакитний -> Світло-блакитний
        }
        bg_color = bg_colors.get(color, '#F3F4F6')
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 12px; border-radius: 8px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>Тип тілобудови: {body_type}</div>
            <div style='font-size: 12px; color: #6B7280; line-height: 1.4;'>{description}</div>
        </div>
        """
        
        if hasattr(self, 'body_type_display'):
            self.body_type_display.setText(result_text)
            self.body_type_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_hr_status_display(self, hr_status_data):
        """Оновлює відображення статусу ЧСС"""
        if not hr_status_data:
            return
        
        status = hr_status_data.get('status', '')
        color = hr_status_data.get('color', '#6B7280')
        description = hr_status_data.get('description', '')
        value = hr_status_data.get('value', 0)
        
        # Визначаємо колір фону
        bg_colors = {
            '#EF4444': '#FEE2E2',  # Червоний -> Світло-червоний
            '#10B981': '#D1FAE5',  # Зелений -> Світло-зелений
            '#F59E0B': '#FEF3C7'   # Помаранчевий -> Світло-помаранчевий
        }
        bg_color = bg_colors.get(color, '#F3F4F6')
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ЧСС: {value} уд/хв</div>
            <div style='font-size: 14px; margin-top: 4px;'>{status}</div>
            <div style='font-size: 12px; color: #6B7280; margin-top: 4px;'>{description}</div>
        </div>
        """
        
        if hasattr(self, 'hr_status_display'):
            self.hr_status_display.setText(result_text)
            self.hr_status_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_hr_zones_display(self, hr_zones_data):
        """Оновлює відображення пульсових зон"""
        if not hr_zones_data:
            return
        
        max_hr = hr_zones_data.get('max_hr', 0)
        zones = ['recovery', 'fat_burn', 'aerobic', 'anaerobic', 'maximum']
        
        zones_html = []
        for zone_key in zones:
            zone = hr_zones_data.get(zone_key, {})
            name = zone.get('name', '')
            range_str = zone.get('range', '')
            percentage = zone.get('percentage', '')
            color = zone.get('color', '#6B7280')
            
            zones_html.append(f"""
                <div style='margin: 4px 0; padding: 6px; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;'>
                    <span style='color: {color}; font-weight: 600;'>{name}</span>
                    <span style='color: #6B7280; margin-left: 8px;'>{range_str} уд/хв ({percentage})</span>
                </div>
            """)
        
        result_text = f"""
        <div style='background: #F8F9FA; padding: 12px; border-radius: 8px;'>
            <div style='font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 8px;'>
                Пульсові зони (макс. {max_hr} уд/хв):
            </div>
            {''.join(zones_html)}
        </div>
        """
        
        if hasattr(self, 'hr_zones_display'):
            self.hr_zones_display.setText(result_text)
            self.hr_zones_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _update_water_intake_display(self, water_intake):
        """Оновлює відображення норми води"""
        if not water_intake:
            return
        
        result_text = f"""
        <div style='background: #E0F2FE; padding: 8px; border-radius: 6px; color: #0891B2; font-weight: 600;'>
            <div style='font-size: 16px;'>Норма води: {water_intake} л/день</div>
        </div>
        """
        
        if hasattr(self, 'water_display'):
            self.water_display.setText(result_text)
            self.water_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _clear_calculations_display(self):
        """Очищає відображення розрахунків при помилках"""
        display_widgets = [
            'bmi_display', 'body_fat_display', 'ideal_weight_display',
            'bmr_display', 'daily_calories_display', 'water_display'
        ]
        
        for widget_name in display_widgets:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                widget.setText("Недостатньо даних для розрахунку")
    
    # ===== ДОПОМІЖНІ МЕТОДИ =====
    
    def _get_group_style(self):
        """Стиль для групових блоків"""
        return """
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #111827;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 8px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
    
    def _load_data(self):
        """Завантажує дані клієнта"""
        if not self.client_data:
            return
        
        self.height_spin.setValue(self.client_data.get('height', 170))
        self.weight_spin.setValue(self.client_data.get('weight', 70.0))
        self.bp_systolic_spin.setValue(self.client_data.get('bp_systolic', 120))
        self.bp_diastolic_spin.setValue(self.client_data.get('bp_diastolic', 80))
        self.heart_rate_spin.setValue(self.client_data.get('heart_rate', 70))
        self.water_intake_spin.setValue(self.client_data.get('water_intake', 2.0))
        self.menstrual_cycle_edit.setText(self.client_data.get('menstrual_cycle', ''))
        
        # Дата медогляду
        if 'medical_exam_date' in self.client_data:
            try:
                exam_date = datetime.fromisoformat(self.client_data['medical_exam_date']).date()
                self.medical_exam_date_edit.setDate(QDate(exam_date))
            except:
                pass
        
        # Медичний дозвіл
        if 'medical_clearance' in self.client_data:
            clearance = self.client_data['medical_clearance']
            for i in range(self.medical_clearance_combo.count()):
                if self.medical_clearance_combo.itemText(i) == clearance:
                    self.medical_clearance_combo.setCurrentIndex(i)
                    break
        
        # 🔥 ВАЖЛИВО: Запускаємо розрахунки після завантаження даних
        # Це забезпечує динамічне відображення всіх показників при відкритті вкладки
        self._update_calculations()
    
    def get_data(self):
        """Повертає дані вкладки"""
        return {
            'height': self.height_spin.value(),
            'weight': self.weight_spin.value(),
            'bp_systolic': self.bp_systolic_spin.value(),
            'bp_diastolic': self.bp_diastolic_spin.value(),
            'heart_rate': self.heart_rate_spin.value(),
            'medical_exam_date': self.medical_exam_date_edit.date().toPython().isoformat(),
            'medical_clearance': self.medical_clearance_combo.currentText(),
            'water_intake': self.water_intake_spin.value(),
            'menstrual_cycle': self.menstrual_cycle_edit.text().strip()
        }
    
    # ===== СПРОЩЕНІ МЕТОДИ РОЗРАХУНКІВ =====
    
    def _calculate_hr_zones_simple(self, age):
        """Спрощений розрахунок пульсових зон"""
        max_hr = 220 - age
        
        result_text = f"""
        <div style='background: #F8F9FA; padding: 12px; border-radius: 8px; color: #374151; font-weight: 600;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>🎯 Максимальний пульс: {max_hr} уд/хв</div>
            <div style='font-size: 14px; margin-bottom: 6px;'>Вік: {age} років</div>
            <div style='font-size: 12px; color: #10B981;'>😌 ВІДНОВЛЕННЯ: {int(max_hr * 0.5)}-{int(max_hr * 0.6)} уд/хв</div>
            <div style='font-size: 12px; color: #F59E0B;'>🔥 ЖИРОСПАЛЮВАННЯ: {int(max_hr * 0.6)}-{int(max_hr * 0.7)} уд/хв</div>
            <div style='font-size: 12px; color: #3B82F6;'>🏃 АЕРОБНА: {int(max_hr * 0.7)}-{int(max_hr * 0.8)} уд/хв</div>
            <div style='font-size: 12px; color: #8B5CF6;'>⚡ АНАЕРОБНА: {int(max_hr * 0.8)}-{int(max_hr * 0.9)} уд/хв</div>
            <div style='font-size: 12px; color: #EF4444;'>🔥 МАКСИМАЛЬНА: {int(max_hr * 0.9)}-{max_hr} уд/хв</div>
        </div>
        """
        
        self.hr_zones_display.setText(result_text)
        self.hr_zones_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_hr_status_simple(self, hr_rest):
        """Спрощений розрахунок статусу ЧСС"""
        if hr_rest < 60:
            status = "✅ Відмінний"
            description = "Дуже добрі показники"
            color = "#10B981"
            bg_color = "#D1FAE5"
        elif hr_rest < 70:
            status = "👍 Хороший"
            description = "Нормальні показники"
            color = "#3B82F6"
            bg_color = "#DBEAFE"
        elif hr_rest < 80:
            status = "📈 Нормальний"
            description = "Середні показники"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        else:
            status = "🔥 Підвищений"
            description = "Потрібно покращити"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ЧСС: {hr_rest} уд/хв</div>
            <div style='font-size: 14px; margin-top: 4px;'>{status}</div>
            <div style='font-size: 12px; color: #6B7280; margin-top: 4px;'>{description}</div>
        </div>
        """
        
        self.hr_status_display.setText(result_text)
        self.hr_status_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_bmi_simple(self, height_cm, weight_kg):
        """Спрощений розрахунок ІМТ"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Недостатня вага"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        elif bmi < 25:
            category = "Нормальна вага"
            color = "#10B981"
            bg_color = "#D1FAE5"
        elif bmi < 30:
            category = "Надмірна вага"
            color = "#F59E0B"
            bg_color = "#FEF3C7"
        else:
            category = "Ожиріння"
            color = "#EF4444"
            bg_color = "#FEE2E2"
        
        result_text = f"""
        <div style='background: {bg_color}; padding: 8px; border-radius: 6px; color: {color}; font-weight: 600;'>
            <div style='font-size: 16px;'>ІМТ: {bmi:.1f}</div>
            <div style='font-size: 14px; margin-top: 4px;'>{category}</div>
        </div>
        """
        
        self.bmi_display.setText(result_text)
        self.bmi_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_bmr_simple(self, height_cm, weight_kg, age, gender):
        """Спрощений розрахунок BMR"""
        if gender == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        result_text = f"""
        <div style='background: #FEF3C7; padding: 8px; border-radius: 6px; color: #D97706; font-weight: 600;'>
            <div style='font-size: 16px;'>BMR: {int(bmr)} ккал/день</div>
            <div style='font-size: 12px; margin-top: 4px; font-weight: normal;'>Базальний метаболізм</div>
        </div>
        """
        
        self.bmr_display.setText(result_text)
        self.bmr_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _calculate_water_simple(self, weight_kg):
        """Спрощений розрахунок норми води"""
        water_liters = round(weight_kg * 0.035, 1)
        
        result_text = f"""
        <div style='background: #E0F2FE; padding: 8px; border-radius: 6px; color: #0891B2; font-weight: 600;'>
            <div style='font-size: 16px;'>Норма води: {water_liters} л/день</div>
            <div style='font-size: 12px; margin-top: 4px; font-weight: normal;'>35 мл на 1 кг ваги</div>
        </div>
        """
        
        self.water_display.setText(result_text)
        self.water_display.setStyleSheet("QLabel { background: transparent; border: none; }")
