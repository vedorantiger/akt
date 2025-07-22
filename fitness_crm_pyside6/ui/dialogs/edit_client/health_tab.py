# ui/dialogs/edit_client/health_tab.py
"""Вкладка здоров'я клієнта"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QScrollArea
from qfluentwidgets import TextEdit, LineEdit


class HealthTab(QWidget):
    """Вкладка здоров'я клієнта"""
    
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
        
        # ===== МЕДИКАМЕНТИ ТА ДОБАВКИ =====
        meds_group = QGroupBox("💊 Медикаменти та добавки")
        meds_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(meds_group)
        
        meds_form = QFormLayout(meds_group)
        meds_form.setSpacing(15)
        meds_form.setContentsMargins(20, 25, 20, 20)
        
        self.medications_edit = TextEdit()
        self.medications_edit.setPlaceholderText("Список ліків, які приймає клієнт")
        self.medications_edit.setMaximumHeight(80)
        meds_form.addRow("💉 Прийом ліків:", self.medications_edit)
        
        self.supplements_edit = TextEdit()
        self.supplements_edit.setPlaceholderText("Список БАДів та добавок")
        self.supplements_edit.setMaximumHeight(80)
        meds_form.addRow("🌿 Прийом БАДів:", self.supplements_edit)
        
        # ===== АЛЕРГІЇ ТА ЗВИЧКИ =====
        allergies_group = QGroupBox("⚠️ Алергії та звички")
        allergies_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(allergies_group)
        
        allergies_form = QFormLayout(allergies_group)
        allergies_form.setSpacing(15)
        allergies_form.setContentsMargins(20, 25, 20, 20)
        
        self.allergies_edit = TextEdit()
        self.allergies_edit.setPlaceholderText("Відомі алергічні реакції")
        self.allergies_edit.setMaximumHeight(80)
        allergies_form.addRow("🤧 Алергії:", self.allergies_edit)
        
        self.bad_habits_edit = TextEdit()
        self.bad_habits_edit.setPlaceholderText("Куріння, алкоголь тощо")
        self.bad_habits_edit.setMaximumHeight(80)
        allergies_form.addRow("🚬 Шкідливі звички:", self.bad_habits_edit)
        
        self.coffee_edit = LineEdit()
        self.coffee_edit.setPlaceholderText("Кількість чашок на день")
        self.coffee_edit.setMinimumHeight(40)
        allergies_form.addRow("☕ Кава на день:", self.coffee_edit)
        
        # ===== ТРАВМИ ТА ЗАХВОРЮВАННЯ =====
        injuries_group = QGroupBox("🏥 Травми та захворювання")
        injuries_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(injuries_group)
        
        injuries_form = QFormLayout(injuries_group)
        injuries_form.setSpacing(15)
        injuries_form.setContentsMargins(20, 25, 20, 20)
        
        self.past_injuries_edit = TextEdit()
        self.past_injuries_edit.setPlaceholderText("Опис минулих травм")
        self.past_injuries_edit.setMaximumHeight(80)
        injuries_form.addRow("🩹 Перенесені травми:", self.past_injuries_edit)
        
        self.current_injuries_edit = TextEdit()
        self.current_injuries_edit.setPlaceholderText("Опис актуальних травм")
        self.current_injuries_edit.setMaximumHeight(80)
        injuries_form.addRow("🆘 Поточні травми:", self.current_injuries_edit)
        
        self.diseases_edit = TextEdit()
        self.diseases_edit.setPlaceholderText("Поточні захворювання та проблеми")
        self.diseases_edit.setMaximumHeight(80)
        injuries_form.addRow("🦠 Захворювання:", self.diseases_edit)
        
        self.contraindications_edit = TextEdit()
        self.contraindications_edit.setPlaceholderText("Медичні протипоказання до фізичних навантажень")
        self.contraindications_edit.setMaximumHeight(80)
        injuries_form.addRow("🚫 Протипоказання:", self.contraindications_edit)
        
        self.complaints_edit = TextEdit()
        self.complaints_edit.setPlaceholderText("Поточні скарги на самопочуття")
        self.complaints_edit.setMaximumHeight(80)
        injuries_form.addRow("😷 Скарги:", self.complaints_edit)
        
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
        
        self.medications_edit.setText(self.client_data.get('medications', ''))
        self.supplements_edit.setText(self.client_data.get('supplements', ''))
        self.allergies_edit.setText(self.client_data.get('allergies', ''))
        self.bad_habits_edit.setText(self.client_data.get('bad_habits', ''))
        self.coffee_edit.setText(self.client_data.get('coffee_per_day', ''))
        self.past_injuries_edit.setText(self.client_data.get('past_injuries', ''))
        self.current_injuries_edit.setText(self.client_data.get('current_injuries', ''))
        self.diseases_edit.setText(self.client_data.get('diseases', ''))
        self.contraindications_edit.setText(self.client_data.get('contraindications', ''))
        self.complaints_edit.setText(self.client_data.get('complaints', ''))
    
    def get_data(self):
        """Повертає дані вкладки"""
        return {
            'medications': self.medications_edit.toPlainText().strip(),
            'supplements': self.supplements_edit.toPlainText().strip(),
            'allergies': self.allergies_edit.toPlainText().strip(),
            'bad_habits': self.bad_habits_edit.toPlainText().strip(),
            'coffee_per_day': self.coffee_edit.text().strip(),
            'past_injuries': self.past_injuries_edit.toPlainText().strip(),
            'current_injuries': self.current_injuries_edit.toPlainText().strip(),
            'diseases': self.diseases_edit.toPlainText().strip(),
            'contraindications': self.contraindications_edit.toPlainText().strip(),
            'complaints': self.complaints_edit.toPlainText().strip()
        }
