# ui/widgets/toast.py
"""Красиві спливаючі повідомлення"""
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont
from qfluentwidgets import FluentIcon as FIF, TransparentToolButton
from enum import Enum


class ToastType(Enum):
    """Типи повідомлень"""
    SUCCESS = ("success", "#4CAF50", FIF.ACCEPT)
    ERROR = ("error", "#F44336", FIF.CLOSE)
    WARNING = ("warning", "#FF9800", FIF.INFO)
    INFO = ("info", "#2196F3", FIF.INFO)


class Toast(QWidget):
    """Красиве спливаюче повідомлення"""
    
    def __init__(self, message: str, toast_type: ToastType = ToastType.INFO, 
                 duration: int = 3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        
        # Налаштування вікна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Ініціалізація UI
        self._init_ui()
        
        # Анімації
        self._init_animations()
        
        # Таймер для автоматичного закриття
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.fade_out)
        self.close_timer.setSingleShot(True)
    
    def _init_ui(self):
        """Створює інтерфейс повідомлення"""
        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Основний layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Іконка
        icon_label = QLabel()
        icon = self.toast_type.value[2].icon()
        icon_label.setPixmap(icon.pixmap(24, 24))
        
        # Текст повідомлення
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        
        # Кнопка закриття
        self.close_btn = TransparentToolButton(FIF.CLOSE, self)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.clicked.connect(self.fade_out)
        self.close_btn.setStyleSheet("""
            TransparentToolButton {
                background-color: transparent;
                border: none;
            }
            TransparentToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        """)
        
        # Додаємо елементи
        layout.addWidget(icon_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_btn)
        
        # Встановлюємо розмір під вміст
        self.adjustSize()
    
    def _init_animations(self):
        """Ініціалізує анімації"""
        # Ефект прозорості
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Анімація появи
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(200)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Анімація зникнення
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self.close)
        
        # Анімація позиції
        self.position_animation = QPropertyAnimation(self, b"pos")
        self.position_animation.setDuration(300)
        self.position_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def paintEvent(self, event):
        """Малює фон повідомлення"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон з заокругленими кутами
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 8, 8)
        
        # Колір фону залежно від типу
        color = QColor(self.toast_type.value[1])
        painter.fillPath(path, color)
        
        # Тінь
        painter.setPen(Qt.NoPen)
        shadow_color = QColor(0, 0, 0, 50)
        for i in range(1, 4):
            shadow_path = QPainterPath()
            shadow_rect = self.rect().adjusted(i, i, i, i)
            shadow_path.addRoundedRect(shadow_rect, 8, 8)
            shadow_color.setAlpha(50 - i * 15)
            painter.fillPath(shadow_path, shadow_color)
    
    def show_toast(self, parent_widget=None):
        """Показує повідомлення"""
        if parent_widget:
            # Позиціонуємо відносно батьківського віджета
            parent_rect = parent_widget.rect()
            parent_pos = parent_widget.mapToGlobal(QPoint(0, 0))
            
            x = parent_pos.x() + (parent_rect.width() - self.width()) // 2
            y = parent_pos.y() + 50
            
            self.move(x, y)
        
        self.show()
        self.fade_in()
        self.close_timer.start(self.duration)
    
    def fade_in(self):
        """Анімація появи"""
        self.fade_in_animation.start()
        
        # Анімація руху вниз
        start_pos = self.pos()
        end_pos = QPoint(start_pos.x(), start_pos.y() + 20)
        
        self.position_animation.setStartValue(start_pos)
        self.position_animation.setEndValue(end_pos)
        self.position_animation.start()
    
    def fade_out(self):
        """Анімація зникнення"""
        self.fade_out_animation.start()
    
    @staticmethod
    def show(message: str, toast_type: ToastType = ToastType.INFO, 
             duration: int = 3000, parent=None):
        """Статичний метод для швидкого показу повідомлення"""
        toast = Toast(message, toast_type, duration, parent)
        toast.show_toast(parent)
        return toast
    
    @staticmethod
    def success(message: str, duration: int = 3000, parent=None):
        """Показати повідомлення про успіх"""
        return Toast.show(message, ToastType.SUCCESS, duration, parent)
    
    @staticmethod
    def error(message: str, duration: int = 3000, parent=None):
        """Показати повідомлення про помилку"""
        return Toast.show(message, ToastType.ERROR, duration, parent)
    
    @staticmethod
    def warning(message: str, duration: int = 3000, parent=None):
        """Показати попередження"""
        return Toast.show(message, ToastType.WARNING, duration, parent)
    
    @staticmethod
    def info(message: str, duration: int = 3000, parent=None):
        """Показати інформаційне повідомлення"""
        return Toast.show(message, ToastType.INFO, duration, parent)