# ui/dialogs/edit_client/physical_tab_new.py
"""Вкладка фізичних параметрів клієнта з автоматичними розрахунками"""
import math
from datetime import datetime, date
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QScrollArea, QLabel, QFrame)
from qfluentwidgets import LineEdit, ComboBox, DateEdit, SpinBox, DoubleSpinBox
from utils.calculations import FitnessCalculator
"""Вкладка фізичних параметрів клієнта з автоматичними розрахунками"""
import math
from datetime import datetime, date
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QGroupBox, QScrollArea, QLabel, QFrame)
from qfluentwidgets import LineEdit, ComboBox, DateEdit, SpinBox, DoubleSpinBox


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
        self.height_spin.setRange(100, 250)
        self.height_spin.setSuffix(" см")
        self.height_spin.setValue(170)
        self.height_spin.setMinimumHeight(40)
        self.height_spin.valueChanged.connect(self._update_calculations)
        basic_form.addRow("📐 Зріст:", self.height_spin)
        
        # Вага
        self.weight_spin = DoubleSpinBox()
        self.weight_spin.setRange(30.0, 300.0)
        self.weight_spin.setDecimals(1)
        self.weight_spin.setSuffix(" кг")
        self.weight_spin.setValue(70.0)
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
        self.bp_systolic_spin.setRange(80, 200)
        self.bp_systolic_spin.setValue(120)
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
        self.bp_diastolic_spin.setRange(50, 150)
        self.bp_diastolic_spin.setValue(80)
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
        self.heart_rate_spin.setRange(40, 200)
        self.heart_rate_spin.setSuffix(" уд/хв")
        self.heart_rate_spin.setValue(70)
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
        if hasattr(self, 'height_spin'):
            self.height_spin.valueChanged.connect(self._update_calculations)
        if hasattr(self, 'weight_spin'):
            self.weight_spin.valueChanged.connect(self._update_calculations)
            self.weight_spin.valueChanged.connect(self._on_weight_changed)
        if hasattr(self, 'heart_rate_spin'):
            self.heart_rate_spin.valueChanged.connect(self._update_calculations)
        
        # Виконуємо початковий розрахунок
        self._update_calculations()
    
    def _on_weight_changed(self, value):
        """Обробляє зміну ваги та сигналізує іншим вкладкам"""
        if hasattr(self, 'weight_changed'):
            self.weight_changed.emit(value)
    
    def _update_calculations(self):
        """Оновлює всі розрахунки автоматично в режимі реального часу"""
        try:
            # Отримуємо базові дані
            height_cm = self.height_spin.value() if self.height_spin.value() > 0 else None
            weight_kg = self.weight_spin.value() if self.weight_spin.value() > 0 else None
            hr_rest = self.heart_rate_spin.value() if self.heart_rate_spin.value() > 0 else None
            
            # Отримуємо дані з інших вкладок
            age = self._get_age()
            gender = self._get_gender()
            activity_level = self._get_activity_level()
            
            # Показуємо/приховуємо поле циклу місячних
            self._toggle_menstrual_field(gender)
            
            # Створюємо словник даних для розрахунків
            data = {
                'weight': weight_kg,
                'height': height_cm,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'hr_rest': hr_rest
            }
            
            # Виконуємо всі розрахунки одночасно
            metrics = FitnessCalculator.calculate_all_metrics(data)
            
            # Оновлюємо відображення всіх результатів (якщо є відповідні віджети)
            if hasattr(self, 'bmi_display'):
                self._update_bmi_display(metrics['bmi'], metrics['bmi_category'])
            if hasattr(self, 'body_fat_display'):
                self._update_body_fat_display(metrics['body_fat_percentage'])
            if hasattr(self, 'ideal_weight_display'):
                self._update_ideal_weight_display(metrics['ideal_weight'])
            if hasattr(self, 'bmr_display'):
                self._update_bmr_display(metrics['bmr'])
            if hasattr(self, 'daily_calories_display'):
                self._update_daily_calories_display(metrics['daily_calories_detailed'])
            if hasattr(self, 'water_display'):
                self._update_water_intake_display(metrics['water_intake'])
            if hasattr(self, 'muscle_mass_display'):
                self._update_muscle_mass_display(metrics['muscle_mass'])
            if hasattr(self, 'body_type_display'):
                self._update_body_type_display(metrics['body_type'])
            if hasattr(self, 'hr_status_display'):
                self._update_hr_status_display(metrics['hr_status'])
            if hasattr(self, 'hr_zones_display'):
                self._update_hr_zones_display(metrics['hr_zones'])
            
        except Exception as e:
            # Логуємо помилку, але не виводимо в консоль
            if hasattr(self, 'parent_dialog') and hasattr(self.parent_dialog, 'logger'):
                self.parent_dialog.logger.error(f"Помилка розрахунків: {e}")
    
    def _update_bmi_display(self, bmi, category):
        """Оновлює відображення ІМТ"""
        if not bmi or not hasattr(self, 'bmi_display'):
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
        if not body_fat or not hasattr(self, 'body_fat_display'):
            return
        
        result_text = f"""
        <div style='background: #DBEAFE; padding: 8px; border-radius: 6px; color: #3B82F6; font-weight: 600;'>
            <div style='font-size: 16px;'>Жир у тілі: {body_fat}%</div>
        </div>
        """
        
        self.body_fat_display.setText(result_text)
        self.body_fat_display.setStyleSheet("QLabel { background: transparent; border: none; }")
    
    def _get_age(self):
        """Отримує вік з вкладки основних даних"""
        try:
            if hasattr(self.parent_dialog, 'basic_tab'):
                birth_date = self.parent_dialog.basic_tab.birth_date_edit.date().toPython()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return age
        except:
            pass
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
        if gender == "female":
            self.menstrual_cycle_edit.setVisible(True)
            self.menstrual_row[0].setVisible(True)  # Лейбл
        else:
            self.menstrual_cycle_edit.setVisible(False)
            self.menstrual_row[0].setVisible(False)  # Лейбл
    
    # ===== МЕТОДИ РОЗРАХУНКІВ =====
    
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
