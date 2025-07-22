# ui/dialogs/edit_client/measurements_tab.py
"""Вкладка замірів клієнта"""
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QScrollArea
from qfluentwidgets import DateEdit, DoubleSpinBox


class MeasurementsTab(QWidget):
    """Вкладка замірів клієнта"""
    
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
        
        # ===== ДАТА ТА ВАГА =====
        basic_group = QGroupBox("📅 Основні дані замірів")
        basic_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(basic_group)
        
        basic_form = QFormLayout(basic_group)
        basic_form.setSpacing(15)
        basic_form.setContentsMargins(20, 25, 20, 20)
        
        self.measurement_date_edit = DateEdit()
        self.measurement_date_edit.setDate(QDate.currentDate())
        self.measurement_date_edit.setMinimumHeight(40)
        basic_form.addRow("📅 Дата замірів:", self.measurement_date_edit)
        
        self.measurement_weight_spin = DoubleSpinBox()
        self.measurement_weight_spin.setRange(30.0, 300.0)
        self.measurement_weight_spin.setDecimals(1)
        self.measurement_weight_spin.setSuffix(" кг")
        self.measurement_weight_spin.setValue(70.0)
        self.measurement_weight_spin.setMinimumHeight(40)
        basic_form.addRow("⚖️ Вага на момент замірів:", self.measurement_weight_spin)
        
        # ===== ОБХВАТИ ТІЛА =====
        circumferences_group = QGroupBox("📏 Обхвати тіла (см)")
        circumferences_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(circumferences_group)
        
        circumferences_form = QFormLayout(circumferences_group)
        circumferences_form.setSpacing(15)
        circumferences_form.setContentsMargins(20, 25, 20, 20)
        
        # Створюємо поля для всіх замірів
        self.measurements = {}
        measurements_list = [
            ("shoulders", "💪 Плечі"),
            ("chest", "🫁 Груди"),
            ("waist", "⏳ Талія"),
            ("hips", "🍑 Стегна"),
            ("left_arm", "💪 Ліва рука"),
            ("right_arm", "💪 Права рука"),
            ("left_thigh", "🦵 Ліве стегно"),
            ("right_thigh", "🦵 Праве стегно"),
            ("left_calf", "🦵 Ліва литка"),
            ("right_calf", "🦵 Права литка")
        ]
        
        for field_name, label in measurements_list:
            spin_box = DoubleSpinBox()
            spin_box.setRange(0.0, 200.0)
            spin_box.setDecimals(1)
            spin_box.setSuffix(" см")
            spin_box.setValue(0.0)
            spin_box.setMinimumHeight(40)
            spin_box.setSpecialValueText("Не виміряно")
            
            circumferences_form.addRow(label, spin_box)
            self.measurements[field_name] = spin_box
        
        content_layout.addStretch()
    
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
    
    def _load_data(self):
        """Завантажує дані клієнта"""
        if not self.client_data:
            return
        
        # Дата замірів
        if 'measurement_date' in self.client_data:
            try:
                measurement_date = QDate.fromString(self.client_data['measurement_date'], "yyyy-MM-dd")
                self.measurement_date_edit.setDate(measurement_date)
            except:
                pass
        
        # Вага на момент замірів
        self.measurement_weight_spin.setValue(self.client_data.get('measurement_weight', 70.0))
        
        # Завантажуємо всі заміри
        for field_name, spin_box in self.measurements.items():
            value = self.client_data.get(field_name, 0.0)
            spin_box.setValue(value)
    
    def get_data(self):
        """Повертає дані вкладки"""
        data = {
            'measurement_date': self.measurement_date_edit.date().toString("yyyy-MM-dd"),
            'measurement_weight': self.measurement_weight_spin.value()
        }
        
        # Додаємо всі заміри
        for field_name, spin_box in self.measurements.items():
            data[field_name] = spin_box.value()
        
        return data
