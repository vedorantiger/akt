# ui/widgets/photo_card.py
"""Красива фотокартка клієнта з детальним дизайном"""
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QGraphicsDropShadowEffect, QPushButton, QFrame, QApplication, QMessageBox)
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont, QLinearGradient
from qfluentwidgets import CardWidget, ImageLabel, CaptionLabel, BodyLabel, StrongBodyLabel
from qfluentwidgets import TransparentToolButton, FluentIcon as FIF, PrimaryPushButton
from ui.styles import COLORS
import os
import webbrowser


class PhotoCard(CardWidget):
    """Детальна фотокартка клієнта 320x620px"""
    
    clicked = Signal(str)  # Сигнал при кліку (передає ID клієнта)
    edit_requested = Signal(str)  # Сигнал для редагування
    view_requested = Signal(str)  # Сигнал для перегляду
    message_requested = Signal(str)  # Сигнал для повідомлень
    ai_requested = Signal(str)  # Сигнал для AI помічника
    delete_requested = Signal(str)  # Сигнал для видалення
    swap_requested = Signal(str, str)  # Сигнал для зміни порядку (source_id, target_id)
    
    def __init__(self, client_data: dict, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        
        # Налагодження ID
        client_id = client_data.get('id', 'NO_ID')
        print(f"🔍 PhotoCard створена з ID: {client_id}")
        
        self.setFixedSize(320, 620)  # Новий розмір відповідно до вимог
        self.setCursor(Qt.PointingHandCursor)
        
        # Налаштування картки
        self.setBorderRadius(16)
        
        # Drag & Drop
        self.setAcceptDrops(True)
        self._drag_start_position = None
        self._is_dragging = False
        
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
        
        # ФОРСОВАНО показуємо картку
        self.show()
        self.setVisible(True)
    
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
        
        # Формуємо повне ім'я з окремих полів
        first_name = self.client_data.get('first_name', '')
        surname = self.client_data.get('surname', '')
        full_name = f"{first_name} {surname}".strip() or 'Без імені'
        
        self.name_label = QLabel(full_name)
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
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.client_data.get('id', '')))
        
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
        self.ai_btn.clicked.connect(self._open_ai_assistant)
        
    def _open_ai_assistant(self):
        """Відкриває персонального АІ помічника для клієнта"""
        # Отримуємо URL AI помічника з даних клієнта
        ai_url = self.client_data.get('ai_url', '').strip()
        
        if ai_url:
            # Якщо посилання збережено - відкриваємо браузер
            try:
                webbrowser.open(ai_url)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Помилка",
                    f"Не вдалося відкрити браузер:\n{str(e)}"
                )
        else:
            # Якщо посилання не налаштовано - показуємо інструкцію
            QMessageBox.information(
                self,
                "АІ помічник не налаштовано",
                "АІ помічник для цього клієнта ще не налаштований.\n\n"
                "Для налаштування:\n"
                "1. Відкрийте редагування клієнта\n"
                "2. Перейдіть на вкладку '🤖 Персональний АІ'\n"
                "3. Створіть та налаштуйте АІ помічника"
            )
    
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
        """Створює стильну заглушку з іконкою камери в бізнес-стилі"""
        pixmap = QPixmap(270, 350)
        pixmap.fill(QColor("#f8f9fa"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Сірий напівпрозорий фон у бізнес-стилі
        gradient = QLinearGradient(0, 0, 270, 350)
        gradient.setColorAt(0, QColor("#e5e7eb"))  # Світло-сірий
        gradient.setColorAt(1, QColor("#d1d5db"))  # Трохи темніший сірий
        
        # Малюємо сірий градієнт
        painter.fillRect(0, 0, 270, 350, gradient)
        
        # Додаємо іконку камери (сірий колір для бізнес-стилю)
        painter.setPen(QColor("#6b7280"))  # Темно-сірий колір
        font = QFont()
        font.setPixelSize(60)
        painter.setFont(font)
        
        painter.drawText(0, 0, 270, 350, Qt.AlignCenter, "📷")
        
        # Додаємо текст "Фото відсутнє" (темно-сірий)
        painter.setPen(QColor("#4b5563"))  # Ще темніший сірий для тексту
        font.setPixelSize(16)
        font.setWeight(QFont.Weight.Medium)  # Трохи жирніший шрифт
        painter.setFont(font)
        painter.drawText(0, 300, 270, 40, Qt.AlignCenter, "Фото відсутнє")
        
        painter.end()
        self.photo_widget.setPixmap(pixmap)
    
    def _init_animations(self):
        """Ініціалізує анімації"""
        # Спрощені анімації для кращої продуктивності
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)  # Скорочено час
        self.scale_animation.setEasingCurve(QEasingCurve.OutQuad)  # Простіша анімація
    
    def enterEvent(self, event):
        """При наведенні миші"""
        super().enterEvent(event)
        
        # Збільшуємо тінь (менш інтенсивно)
        self.shadow.setBlurRadius(30)  # Менше blur
        self.shadow.setOffset(0, 8)    # Менший зсув
        
        # Легка анімація підйому (менший масштаб)
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x() - 2,  # Менший зсув
            current_rect.y() - 2,
            current_rect.width() + 4,
            current_rect.height() + 4
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
        
        # Повертаємо розмір (менший зсув)
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x() + 2,  # Менший зсув
            current_rect.y() + 2,
            current_rect.width() - 4,
            current_rect.height() - 4
        )
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(new_rect)
        self.scale_animation.start()
    
    def mousePressEvent(self, event):
        """При кліку на картку"""
        if event.button() == Qt.LeftButton:
            self._drag_start_position = event.position()
            self.clicked.emit(self.client_data.get('id', ''))
        event.accept()
    
    def mouseMoveEvent(self, event):
        """Обробка руху миші для drag & drop"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if not self._drag_start_position:
            return
        
        # Перевіряємо чи досить далеко пересунули
        distance = (event.position() - self._drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return
        
        # Починаємо перетягування
        self._start_drag(event)
    
    def mouseReleaseEvent(self, event):
        """При відпусканні кнопки миші"""
        self._drag_start_position = None
        self._is_dragging = False
        event.accept()
    
    def _start_drag(self, event):
        """Починає операцію перетягування"""
        from PySide6.QtGui import QDrag, QPixmap, QPainter
        from PySide6.QtCore import QMimeData
        
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Зберігаємо ID клієнта в MIME данных
        mime_data.setText(self.client_data.get('id', ''))
        drag.setMimeData(mime_data)
        
        # Створюємо превью для перетягування
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        
        # Робимо превью напівпрозорим
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(Qt.transparent)
        
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        drag.setPixmap(transparent_pixmap)
        drag.setHotSpot(event.position().toPoint())
        
        # Змінюємо стиль картки під час перетягування
        self._is_dragging = True
        self.setStyleSheet(self.styleSheet() + """
            PhotoCard {
                border: 2px dashed #3B82F6;
                background-color: rgba(59, 130, 246, 0.1);
            }
        """)
        
        # Виконуємо перетягування
        drop_action = drag.exec_(Qt.MoveAction)
        
        # Відновлюємо стиль
        self._is_dragging = False
        self.setStyleSheet("")
    
    def dragEnterEvent(self, event):
        """Коли перетягуване входить в область картки"""
        if event.mimeData().hasText() and not self._is_dragging:
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet() + """
                PhotoCard {
                    border: 2px solid #10B981;
                    background-color: rgba(16, 185, 129, 0.1);
                }
            """)
    
    def dragMoveEvent(self, event):
        """Коли перетягування рухається над карткою"""
        if event.mimeData().hasText() and not self._is_dragging:
            event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """Коли перетягування покидає область картки"""
        self.setStyleSheet("")
    
    def dropEvent(self, event):
        """Коли відбувається падіння на картку"""
        if event.mimeData().hasText() and not self._is_dragging:
            source_id = event.mimeData().text()
            target_id = self.client_data.get('id', '')
            
            if source_id != target_id:
                self.swap_requested.emit(source_id, target_id)
            
            event.acceptProposedAction()
        
        # Відновлюємо стиль
        self.setStyleSheet("")
        event.accept()
    
    def updateCardData(self, new_client_data: dict):
        """Оновлює дані картки без перестворення layout"""
        self.client_data = new_client_data
        
        # Оновлюємо ім'я клієнта
        if hasattr(self, 'name_label'):
            first_name = new_client_data.get('first_name', '')
            surname = new_client_data.get('surname', '')
            full_name = f"{first_name} {surname}".strip() or 'Без імені'
            self.name_label.setText(full_name)
        
        # Оновлюємо телефон
        if hasattr(self, 'phone_label'):
            phone = new_client_data.get('phone', 'Телефон не вказано')
            self.phone_label.setText(phone)
        
        # Оновлюємо фото клієнта
        if hasattr(self, 'photo_widget'):
            self._load_photo()
        
        print(f"🔄 PhotoCard оновлена для клієнта: {new_client_data.get('full_name', full_name)}")
    
    def _get_client_photo_path(self):
        """Отримує шлях до фото клієнта"""
        return self.client_data.get('photo_path')
