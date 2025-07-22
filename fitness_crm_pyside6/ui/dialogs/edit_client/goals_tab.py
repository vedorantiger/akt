# ui/dialogs/edit_client/goals_tab.py
"""Вкладка цілей та планів клієнта"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox, 
                               QScrollArea, QCheckBox, QGridLayout)
from qfluentwidgets import TextEdit, SpinBox, ComboBox


class GoalsTab(QWidget):
    """Вкладка цілей та планів клієнта"""
    
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
        
        # ===== ЦІЛІ =====
        goals_group = QGroupBox("🎯 Поставлені цілі")
        goals_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(goals_group)
        
        goals_form = QFormLayout(goals_group)
        goals_form.setSpacing(15)
        goals_form.setContentsMargins(20, 25, 20, 20)
        
        self.goals_edit = TextEdit()
        self.goals_edit.setPlaceholderText("Детальний опис фітнес-цілей клієнта")
        self.goals_edit.setMinimumHeight(120)
        goals_form.addRow("📝 Цілі клієнта:", self.goals_edit)
        
        # ===== ПЛАНИ ТРЕНУВАНЬ =====
        training_group = QGroupBox("💪 Плани тренувань")
        training_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(training_group)
        
        training_form = QFormLayout(training_group)
        training_form.setSpacing(15)
        training_form.setContentsMargins(20, 25, 20, 20)
        
        self.workouts_per_week_spin = SpinBox()
        self.workouts_per_week_spin.setRange(1, 7)
        self.workouts_per_week_spin.setValue(3)
        self.workouts_per_week_spin.setSuffix(" тренувань")
        self.workouts_per_week_spin.setMinimumHeight(40)
        training_form.addRow("📅 Тренувань на тиждень:", self.workouts_per_week_spin)
        
        self.preferred_training_combo = ComboBox()
        self.preferred_training_combo.addItems([
            "Групові тренування",
            "Індивідуальні тренування",
            "Без різниці"
        ])
        self.preferred_training_combo.setMinimumHeight(40)
        training_form.addRow("👥 Бажані заняття:", self.preferred_training_combo)
        
        # ===== ВИДИ АКТИВНОСТІ =====
        activities_group = QGroupBox("🏃 Бажані види активності")
        activities_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(activities_group)
        
        activities_layout = QVBoxLayout(activities_group)
        activities_layout.setContentsMargins(20, 25, 20, 20)
        
        # Створюємо сітку чекбоксів для видів активності
        activities_grid = QGridLayout()
        
        self.activity_checkboxes = {}
        activities = [
            "💪 Силові тренування",
            "🏃 Кардіо тренування",
            "🧘 Пілатес",
            "🤸 Кросфіт",
            "🥊 Бокс",
            "🤾 Функціональні тренування",
            "🏊 Плавання",
            "🚴 Велотренування",
            "🤲 Йога",
            "💃 Танці",
            "🏐 Командні види спорту",
            "🏃‍♀️ Біг",
            "🤸‍♀️ Гімнастика",
            "🏋️ Пауерліфтинг",
            "🧗 Скелелазіння",
            "🏄 Серфінг/Скейт"
        ]
        
        for i, activity in enumerate(activities):
            checkbox = QCheckBox(activity)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #374151;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #D1D5DB;
                }
                QCheckBox::indicator:checked {
                    background-color: #3B82F6;
                    border-color: #3B82F6;
                }
            """)
            row = i // 4
            col = i % 4
            activities_grid.addWidget(checkbox, row, col)
            self.activity_checkboxes[activity] = checkbox
        
        activities_layout.addLayout(activities_grid)
        
        # ===== НОТАТКИ ТРЕНЕРА =====
        notes_group = QGroupBox("📝 Нотатки тренера")
        notes_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(notes_group)
        
        notes_form = QFormLayout(notes_group)
        notes_form.setSpacing(15)
        notes_form.setContentsMargins(20, 25, 20, 20)
        
        self.trainer_notes_edit = TextEdit()
        self.trainer_notes_edit.setPlaceholderText("Додаткові нотатки та спостереження тренера")
        self.trainer_notes_edit.setMinimumHeight(120)
        notes_form.addRow("💭 Нотатки:", self.trainer_notes_edit)
        
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
        
        self.goals_edit.setText(self.client_data.get('goals', ''))
        self.workouts_per_week_spin.setValue(self.client_data.get('workouts_per_week', 3))
        
        preferred_training = self.client_data.get('preferred_training', '')
        if preferred_training in ['Групові тренування', 'Індивідуальні тренування', 'Без різниці']:
            self.preferred_training_combo.setCurrentText(preferred_training)
        
        # Завантажуємо вибрані види активності
        selected_activities = self.client_data.get('selected_activities', [])
        for activity, checkbox in self.activity_checkboxes.items():
            checkbox.setChecked(activity in selected_activities)
        
        self.trainer_notes_edit.setText(self.client_data.get('trainer_notes', ''))
    
    def get_data(self):
        """Повертає дані вкладки"""
        # Збираємо вибрані види активності
        selected_activities = []
        for activity, checkbox in self.activity_checkboxes.items():
            if checkbox.isChecked():
                selected_activities.append(activity)
        
        return {
            'goals': self.goals_edit.toPlainText().strip(),
            'workouts_per_week': self.workouts_per_week_spin.value(),
            'preferred_training': self.preferred_training_combo.currentText(),
            'selected_activities': selected_activities,
            'trainer_notes': self.trainer_notes_edit.toPlainText().strip()
        }
