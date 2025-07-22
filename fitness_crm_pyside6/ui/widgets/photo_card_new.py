# ui/widgets/photo_card.py
"""Красива фотокартка клієнта з детальним дизайном"""
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QGraphicsDropShadowEffect, QPushButton, QFrame)
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont, QLinearGradient
from qfluentwidgets import CardWidget, ImageLabel, CaptionLabel, BodyLabel, StrongBodyLabel
from qfluentwidgets import TransparentToolButton, FluentIcon as FIF, PrimaryPushButton
from ui.styles import COLORS, get_button_style
import os


class PhotoCard(CardWidget):
    """Детальна фотокартка клієнта 320x620px"""
    
    clicked = Signal(str)  # Сигнал при кліку (передає ID клієнта)
    edit_requested = Signal(str)  # Сигнал для редагування
    view_requested = Signal(str)  # Сигнал для перегляду
    message_requested = Signal(str)  # Сигнал для повідомлень
    ai_requested = Signal(str)  # Сигнал для AI помічника
    
    def __init__(self, client_data: dict, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        self.setFixedSize(320, 620)  # Новий розмір відповідно до вимог
        self.setCursor(Qt.PointingHandCursor)
        
        # Налаштування картки
        self.setBorderRadius(16)
        
        # Створюємо тінь
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(25)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 6)
        self.setGraphicsEffect(self.shadow)
        
        # Ініціалізуємо UI
        self._init_ui()
        
        # Анімація при наведенні
        self._init_animations()
    
    def _init_ui(self):
        """Створює інтерфейс картки з новим дизайном"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # ===== СЕКЦІЯ ФОТОГРАФІЇ (270x350px) =====
        self.photo_container = QFrame()
        self.photo_container.setFixedSize(270, 350)
        self.photo_container.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
            }
        """)
        
        # Layout для фото секції
        photo_layout = QVBoxLayout(self.photo_container)
        photo_layout.setContentsMargins(0, 0, 0, 0)
        photo_layout.setAlignment(Qt.AlignCenter)
        
        # Фото або іконка
        self.photo_widget = QLabel()
        self.photo_widget.setFixedSize(270, 350)
        self.photo_widget.setAlignment(Qt.AlignCenter)
        self.photo_widget.setStyleSheet("border: none; border-radius: 10px;")
        
        # Завантажуємо фото або встановлюємо заглушку
        self._load_photo()
        
        photo_layout.addWidget(self.photo_widget)
        
        # Кнопки редагування у правому верхньому куті фото
        self._create_photo_action_buttons()
        
        # ===== ІМ'Я КЛІЄНТА (270x48px) =====
        self.name_container = QFrame()
        self.name_container.setFixedSize(270, 48)
        self.name_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        
        name_layout = QVBoxLayout(self.name_container)
        name_layout.setContentsMargins(12, 0, 12, 0)
        name_layout.setAlignment(Qt.AlignCenter)
        
        self.name_label = QLabel(self.client_data.get('full_name', 'Без імені'))
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                background: transparent;
                border: none;
            }
        """)
        self.name_label.setAlignment(Qt.AlignCenter)
        name_layout.addWidget(self.name_label)
        
        # ===== ТЕЛЕФОН КЛІЄНТА (270x42px) =====
        self.phone_container = QFrame()
        self.phone_container.setFixedSize(270, 42)
        self.phone_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        
        phone_layout = QVBoxLayout(self.phone_container)
        phone_layout.setContentsMargins(12, 0, 12, 0)
        phone_layout.setAlignment(Qt.AlignCenter)
        
        self.phone_label = QLabel(self.client_data.get('phone', 'Телефон не вказано'))
        self.phone_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 500;
                color: #374151;
                background: transparent;
                border: none;
            }
        """)
        self.phone_label.setAlignment(Qt.AlignCenter)
        phone_layout.addWidget(self.phone_label)
        
        # ===== КНОПКИ ДІЙ =====
        self._create_action_buttons()
        
        # Додаємо всі секції до головного layout
        main_layout.addWidget(self.photo_container, 0, Qt.AlignCenter)
        main_layout.addWidget(self.name_container, 0, Qt.AlignCenter)
        main_layout.addWidget(self.phone_container, 0, Qt.AlignCenter)
        main_layout.addWidget(self.action_buttons_container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
    def _create_photo_action_buttons(self):
        """Створює кнопки редагування у правому верхньому куті фото"""
        # Контейнер для кнопок
        buttons_widget = QWidget(self.photo_container)
        buttons_widget.setFixedSize(80, 40)
        buttons_widget.move(185, 10)  # Позиціонуємо у правому верхньому куті
        
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(5)
        
        # Кнопка видалення
        self.delete_btn = TransparentToolButton(FIF.DELETE)
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setToolTip("Видалити клієнта")
        self.delete_btn.setStyleSheet("""
            TransparentToolButton {
                background: rgba(239, 68, 68, 0.8);
                border-radius: 15px;
            }
            TransparentToolButton:hover {
                background: rgba(239, 68, 68, 1.0);
            }
        """)
        
        # Кнопка редагування
        self.edit_photo_btn = TransparentToolButton(FIF.EDIT)
        self.edit_photo_btn.setFixedSize(30, 30)
        self.edit_photo_btn.setToolTip("Редагувати клієнта")
        self.edit_photo_btn.setStyleSheet("""
            TransparentToolButton {
                background: rgba(59, 130, 246, 0.8);
                border-radius: 15px;
            }
            TransparentToolButton:hover {
                background: rgba(59, 130, 246, 1.0);
            }
        """)
        
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.edit_photo_btn)
        
        # Підключаємо сигнали
        self.edit_photo_btn.clicked.connect(lambda: self.edit_requested.emit(self.client_data.get('id', '')))
        
    def _create_action_buttons(self):
        """Створює основні кнопки дій внизу картки"""
        self.action_buttons_container = QWidget()
        self.action_buttons_container.setFixedSize(270, 120)
        
        buttons_layout = QVBoxLayout(self.action_buttons_container)
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        buttons_layout.setSpacing(8)
        
        # Кнопка "ВЕДЕННЯ"
        self.view_btn = QPushButton("📊 ВЕДЕННЯ")
        self.view_btn.setFixedSize(270, 36)
        self.view_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: #2563eb;
            }}
            QPushButton:pressed {{
                background: #1d4ed8;
            }}
        """)
        
        # Кнопка "ПОВІДОМЛЕННЯ"
        self.message_btn = QPushButton("💬 ПОВІДОМЛЕННЯ")
        self.message_btn.setFixedSize(270, 36)
        self.message_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['secondary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: #7c3aed;
            }}
            QPushButton:pressed {{
                background: #6d28d9;
            }}
        """)
        
        # Кнопка "АІ ПОМІЧНИК"
        self.ai_btn = QPushButton("🤖 АІ ПОМІЧНИК")
        self.ai_btn.setFixedSize(270, 36)
        self.ai_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['info']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: #0ea5e9;
            }}
            QPushButton:pressed {{
                background: #0284c7;
            }}
        """)
        
        # Додаємо кнопки
        buttons_layout.addWidget(self.view_btn)
        buttons_layout.addWidget(self.message_btn)
        buttons_layout.addWidget(self.ai_btn)
        
        # Підключаємо сигнали (поки що заглушки)
        self.view_btn.clicked.connect(lambda: self._show_development_message("ВЕДЕННЯ"))
        self.message_btn.clicked.connect(lambda: self._show_development_message("ПОВІДОМЛЕННЯ"))
        self.ai_btn.clicked.connect(lambda: self._show_development_message("АІ ПОМІЧНИК"))
        
    def _show_development_message(self, feature_name):
        """Показує повідомлення про розробку"""
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.info(
            title="В розробці",
            content=f"Функція '{feature_name}' знаходиться в розробці",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.window()
        )
    
    def _load_photo(self):
        """Завантажує фото клієнта або встановлює заглушку"""
        photo_path = self.client_data.get('photo_path')
        
        if photo_path and os.path.exists(photo_path):
            # Завантажуємо реальне фото
            pixmap = QPixmap(photo_path)
            
            # Масштабуємо зображення до розміру з збереженням пропорцій
            scaled_pixmap = pixmap.scaled(
                270, 350, 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Обрізаємо зображення по центру, якщо воно більше за розмір
            if scaled_pixmap.width() > 270 or scaled_pixmap.height() > 350:
                x = (scaled_pixmap.width() - 270) // 2
                y = (scaled_pixmap.height() - 350) // 2
                scaled_pixmap = scaled_pixmap.copy(x, y, 270, 350)
                
            self.photo_widget.setPixmap(scaled_pixmap)
        else:
            # Створюємо красиву заглушку
            self._create_photo_placeholder()
            
    def _create_photo_placeholder(self):
        """Створює красиву заглушку з іконкою камери"""
        pixmap = QPixmap(270, 350)
        pixmap.fill(QColor("#f8f9fa"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Градієнтний фон
        gradient = QLinearGradient(0, 0, 270, 350)
        colors = [
            ("#667eea", "#764ba2"),  # Фіолетовий
            ("#f093fb", "#f5576c"),  # Рожевий
            ("#4facfe", "#00f2fe"),  # Блакитний
            ("#43e97b", "#38f9d7"),  # Зелений
            ("#fa709a", "#fee140"),  # Жовто-рожевий
        ]
        
        # Вибираємо колір на основі імені
        name = self.client_data.get('full_name', '')
        color_index = sum(ord(c) for c in name) % len(colors) if name else 0
        start_color, end_color = colors[color_index]
        
        gradient.setColorAt(0, QColor(start_color))
        gradient.setColorAt(1, QColor(end_color))
        
        # Малюємо градієнт
        painter.fillRect(0, 0, 270, 350, gradient)
        
        # Додаємо іконку камери
        painter.setPen(QColor("white"))
        font = QFont()
        font.setPixelSize(60)
        painter.setFont(font)
        
        painter.drawText(0, 0, 270, 350, Qt.AlignCenter, "📷")
        
        # Додаємо текст "Без фото"
        font.setPixelSize(16)
        painter.setFont(font)
        painter.drawText(0, 300, 270, 40, Qt.AlignCenter, "Без фото")
        
        painter.end()
        self.photo_widget.setPixmap(pixmap)
    
    def _init_animations(self):
        """Ініціалізує анімації"""
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        """При наведенні миші"""
        super().enterEvent(event)
        
        # Збільшуємо тінь
        self.shadow.setBlurRadius(35)
        self.shadow.setOffset(0, 10)
        
        # Легка анімація підйому
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x() - 3,
            current_rect.y() - 3,
            current_rect.width() + 6,
            current_rect.height() + 6
        )
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(new_rect)
        self.scale_animation.start()
    
    def leaveEvent(self, event):
        """При покиданні миші"""
        super().leaveEvent(event)
        
        # Зменшуємо тінь
        self.shadow.setBlurRadius(25)
        self.shadow.setOffset(0, 6)
        
        # Повертаємо розмір
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x() + 3,
            current_rect.y() + 3,
            current_rect.width() - 6,
            current_rect.height() - 6
        )
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(new_rect)
        self.scale_animation.start()
    
    def mousePressEvent(self, event):
        """При кліку на картку"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.client_data.get('id', ''))
        # Не викликаємо super(), щоб уникнути конфлікту сигналів
        event.accept()
    
    def mouseReleaseEvent(self, event):
        """При відпусканні кнопки миші"""
        # Не викликаємо super(), щоб уникнути конфлікту сигналів
        event.accept()
    
    def updateCardData(self, new_client_data: dict):
        """Оновлює дані картки та перемальовує інтерфейс"""
        self.client_data = new_client_data
        
        # Очищаємо поточний layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Перемальовуємо інтерфейс з новими даними
        self._init_ui()
        
        print(f"🔄 PhotoCard оновлена для клієнта: {new_client_data.get('full_name', 'Невідомий')}")
