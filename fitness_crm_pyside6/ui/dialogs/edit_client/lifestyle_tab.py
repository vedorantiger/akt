# ui/dialogs/edit_client/lifestyle_tab.py
"""Вкладка способу життя клієнта"""
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QScrollArea
from qfluentwidgets import ComboBox, TextEdit, LineEdit, TimeEdit, SpinBox


class LifestyleTab(QWidget):
    """Вкладка способу життя клієнта"""
    
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
        
        # ===== АКТИВНІСТЬ ТА ХАРЧУВАННЯ =====
        activity_group = QGroupBox("🏃 Активність та харчування")
        activity_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(activity_group)
        
        activity_form = QFormLayout(activity_group)
        activity_form.setSpacing(15)
        activity_form.setContentsMargins(20, 25, 20, 20)
        
        self.activity_level_combo = ComboBox()
        self.activity_level_combo.addItems([
            "Сидячий спосіб життя",
            "Малоактивний",
            "Помірно активний",
            "Активний",
            "Дуже активний"
        ])
        self.activity_level_combo.setMinimumHeight(40)
        activity_form.addRow("📊 Рівень активності:", self.activity_level_combo)
        
        self.food_preferences_edit = TextEdit()
        self.food_preferences_edit.setPlaceholderText("Дієтичні обмеження, уподобання")
        self.food_preferences_edit.setMaximumHeight(80)
        activity_form.addRow("🍽️ Харчові вподобання:", self.food_preferences_edit)
        
        # ===== РЕЖИМ ДНЯ =====
        schedule_group = QGroupBox("🕐 Режим дня")
        schedule_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(schedule_group)
        
        schedule_form = QFormLayout(schedule_group)
        schedule_form.setSpacing(15)
        schedule_form.setContentsMargins(20, 25, 20, 20)
        
        self.wake_time_edit = TimeEdit()
        self.wake_time_edit.setTime(QTime(7, 0))
        self.wake_time_edit.setMinimumHeight(40)
        schedule_form.addRow("🌅 Час підйому:", self.wake_time_edit)
        
        self.sleep_time_edit = TimeEdit()
        self.sleep_time_edit.setTime(QTime(23, 0))
        self.sleep_time_edit.setMinimumHeight(40)
        schedule_form.addRow("🌙 Час засинання:", self.sleep_time_edit)
        
        self.sleep_duration_spin = SpinBox()
        self.sleep_duration_spin.setRange(4, 12)
        self.sleep_duration_spin.setValue(8)
        self.sleep_duration_spin.setSuffix(" годин")
        self.sleep_duration_spin.setMinimumHeight(40)
        schedule_form.addRow("⏰ Тривалість сну:", self.sleep_duration_spin)
        
        self.sleep_quality_combo = ComboBox()
        self.sleep_quality_combo.addItems([
            "Погана", "Задовільна", "Хороша", "Відмінна"
        ])
        self.sleep_quality_combo.setMinimumHeight(40)
        schedule_form.addRow("💤 Якість сну:", self.sleep_quality_combo)
        
        self.night_awakenings_spin = SpinBox()
        self.night_awakenings_spin.setRange(0, 10)
        self.night_awakenings_spin.setValue(0)
        self.night_awakenings_spin.setSuffix(" разів")
        self.night_awakenings_spin.setMinimumHeight(40)
        schedule_form.addRow("🌜 Прокидання вночі:", self.night_awakenings_spin)
        
        # ===== СПОРТИВНИЙ ДОСВІД =====
        sports_group = QGroupBox("🏆 Спортивний досвід")
        sports_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(sports_group)
        
        sports_form = QFormLayout(sports_group)
        sports_form.setSpacing(15)
        sports_form.setContentsMargins(20, 25, 20, 20)
        
        self.other_sports_edit = TextEdit()
        self.other_sports_edit.setPlaceholderText("Вид та частота інших видів спорту")
        self.other_sports_edit.setMaximumHeight(80)
        sports_form.addRow("⚽ Інші заняття спортом:", self.other_sports_edit)
        
        self.past_experience_edit = TextEdit()
        self.past_experience_edit.setPlaceholderText("Попередній спортивний досвід")
        self.past_experience_edit.setMaximumHeight(80)
        sports_form.addRow("📚 Минулий досвід:", self.past_experience_edit)
        
        self.fitness_level_combo = ComboBox()
        self.fitness_level_combo.addItems([
            "Низька", "Середня", "Висока"
        ])
        self.fitness_level_combo.setMinimumHeight(40)
        sports_form.addRow("💪 Фізична підготовка:", self.fitness_level_combo)
        
        self.motivation_level_combo = ComboBox()
        self.motivation_level_combo.addItems([
            "Низька", "Середня", "Висока"
        ])
        self.motivation_level_combo.setMinimumHeight(40)
        sports_form.addRow("🔥 Мотивація:", self.motivation_level_combo)
        
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
        
        # Рівень активності
        activity_level = self.client_data.get('activity_level', '')
        if activity_level in ['Сидячий спосіб життя', 'Малоактивний', 'Помірно активний', 'Активний', 'Дуже активний']:
            self.activity_level_combo.setCurrentText(activity_level)
        
        self.food_preferences_edit.setText(self.client_data.get('food_preferences', ''))
        
        # Режим дня
        if 'wake_time' in self.client_data:
            try:
                wake_time = QTime.fromString(self.client_data['wake_time'], "hh:mm")
                self.wake_time_edit.setTime(wake_time)
            except:
                pass
        
        if 'sleep_time' in self.client_data:
            try:
                sleep_time = QTime.fromString(self.client_data['sleep_time'], "hh:mm")
                self.sleep_time_edit.setTime(sleep_time)
            except:
                pass
        
        self.sleep_duration_spin.setValue(self.client_data.get('sleep_duration', 8))
        
        sleep_quality = self.client_data.get('sleep_quality', '')
        if sleep_quality in ['Погана', 'Задовільна', 'Хороша', 'Відмінна']:
            self.sleep_quality_combo.setCurrentText(sleep_quality)
        
        self.night_awakenings_spin.setValue(self.client_data.get('night_awakenings', 0))
        
        # Спорт
        self.other_sports_edit.setText(self.client_data.get('other_sports', ''))
        self.past_experience_edit.setText(self.client_data.get('past_experience', ''))
        
        fitness_level = self.client_data.get('fitness_level', '')
        if fitness_level in ['Низька', 'Середня', 'Висока']:
            self.fitness_level_combo.setCurrentText(fitness_level)
        
        motivation_level = self.client_data.get('motivation_level', '')
        if motivation_level in ['Низька', 'Середня', 'Висока']:
            self.motivation_level_combo.setCurrentText(motivation_level)
    
    def get_data(self):
        """Повертає дані вкладки"""
        return {
            'activity_level': self.activity_level_combo.currentText(),
            'food_preferences': self.food_preferences_edit.toPlainText().strip(),
            'wake_time': self.wake_time_edit.time().toString("hh:mm"),
            'sleep_time': self.sleep_time_edit.time().toString("hh:mm"),
            'sleep_duration': self.sleep_duration_spin.value(),
            'sleep_quality': self.sleep_quality_combo.currentText(),
            'night_awakenings': self.night_awakenings_spin.value(),
            'other_sports': self.other_sports_edit.toPlainText().strip(),
            'past_experience': self.past_experience_edit.toPlainText().strip(),
            'fitness_level': self.fitness_level_combo.currentText(),
            'motivation_level': self.motivation_level_combo.currentText()
        }
