# ui/dialogs/photo_display.py
"""Віджет для відображення та редагування фото клієнта"""
from PySide6.QtCore import Signal, QRect, Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen


class PhotoDisplayWidget(QWidget):
    """Віджет для відображення та налаштування фото клієнта"""
    
    photo_changed = Signal(str)  # Сигнал зміни фото
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Дані фото
        self.photo_path = None
        self.pixmap = None
        self._scale = 1.0  # Поточний масштаб
        self._offset = None  # Зміщення як QPointF
        
        # Початкові параметри позиціонування
        self.photo_scale = 1.0
        self.photo_offset_x = 0
        self.photo_offset_y = 0
        
        # Налаштування зображення
        self.brightness = 0
        self.contrast = 0
        self.saturation = 0
        self.sharpness = 0
        
        # Прапорці для перетягування
        self.dragging = False
        self.last_pan_point = None
        
        # Мінімальний та максимальний масштаб
        self.min_scale = 0.1
        self.max_scale = 5.0
        
        self._init_ui()
        
    def _init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setMinimumSize(280, 350)
        self.setStyleSheet("""
            PhotoDisplayWidget {
                background-color: #FAFAFA;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        
        # Показуємо заглушку спочатку
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Показує заглушку коли фото немає"""
        self.photo_path = None
        self.pixmap = None
        self.update()
    
    def load_photo(self, photo_path):
        """Завантажує фото за шляхом"""
        try:
            self.photo_path = photo_path
            self.pixmap = QPixmap(photo_path)
            
            if self.pixmap.isNull():
                self._show_placeholder()
                return False
            
            # Скидаємо трансформації тільки якщо не встановлені збережені параметри
            if self._scale == 1.0 and (not self._offset or (self._offset.x() == 0 and self._offset.y() == 0)):
                # Автоматично підганяємо фото
                self._auto_fit_photo()
            else:
                # Використовуємо збережені параметри
                self._scale = self.photo_scale
                from PySide6.QtCore import QPointF
                if not self._offset:
                    self._offset = QPointF(self.photo_offset_x, self.photo_offset_y)
                else:
                    self._offset.setX(self.photo_offset_x)
                    self._offset.setY(self.photo_offset_y)
            
            self.update()
            self.photo_changed.emit(photo_path)
            return True
            
        except (OSError, IOError) as e:
            print(f"Помилка завантаження фото: {e}")
            self._show_placeholder()
            return False
    
    def _fit_to_widget(self):
        """Підганяє фото під розмір віджета"""
        if not self.pixmap:
            return
        
        widget_rect = self.rect()
        pixmap_rect = self.pixmap.rect()
        
        # Обчислюємо масштаб для вміщення
        scale_x = widget_rect.width() / pixmap_rect.width()
        scale_y = widget_rect.height() / pixmap_rect.height()
        
        self.photo_scale = min(scale_x, scale_y) * 0.9  # Трохи зменшуємо для відступів
        
        # Центруємо
        scaled_width = pixmap_rect.width() * self.photo_scale
        scaled_height = pixmap_rect.height() * self.photo_scale
        
        self.photo_offset_x = (widget_rect.width() - scaled_width) / 2
        self.photo_offset_y = (widget_rect.height() - scaled_height) / 2
    
    def paintEvent(self, event):
        """Малює віджет"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        if self.pixmap and not self.pixmap.isNull():
            self._draw_photo(painter)
        else:
            self._draw_placeholder(painter)
    
    def _draw_photo(self, painter):
        """Малює фото з трансформаціями"""
        if not self.pixmap or not self._offset:
            return
        
        # Обчислюємо розміри та позицію
        scaled_width = int(self.pixmap.width() * self._scale)
        scaled_height = int(self.pixmap.height() * self._scale)
        
        x = int(self._offset.x())
        y = int(self._offset.y())
        
        # Малюємо фото
        target_rect = QRect(x, y, scaled_width, scaled_height)
        painter.drawPixmap(target_rect, self.pixmap)
    
    def _draw_placeholder(self, painter):
        """Малює заглушку коли фото немає"""
        rect = self.rect()
        
        # Фон
        painter.fillRect(rect, QColor("#FAFAFA"))
        
        # Іконка камери
        painter.setPen(QPen(QColor("#6B7280"), 2))
        font = QFont()
        font.setPointSize(48)
        painter.setFont(font)
        
        camera_text = "📷"
        camera_rect = painter.fontMetrics().boundingRect(camera_text)
        camera_x = (rect.width() - camera_rect.width()) // 2
        camera_y = (rect.height() // 2) - 20
        
        painter.drawText(camera_x, camera_y, camera_text)
        
        # Текст
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#4B5563"))
        
        text = "ФОТО"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = (rect.width() - text_rect.width()) // 2
        text_y = camera_y + 60
        
        painter.drawText(text_x, text_y, text)
    
    def wheelEvent(self, event):
        """Обробка прокрутки миші для зуму"""
        if not self.pixmap or not self._offset:
            return
        
        # Зум
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 1.0 / 1.1
        
        # Обмежуємо масштаб
        new_scale = self._scale * zoom_factor
        if self.min_scale <= new_scale <= self.max_scale:
            # Зум до позиції курсора
            mouse_pos = event.position()
            
            # Зберігаємо відносну позицію курсора
            rel_x = (mouse_pos.x() - self._offset.x()) / (self.pixmap.width() * self._scale)
            rel_y = (mouse_pos.y() - self._offset.y()) / (self.pixmap.height() * self._scale)
            
            self._scale = new_scale
            
            # Коригуємо зміщення
            self._offset.setX(mouse_pos.x() - (rel_x * self.pixmap.width() * self._scale))
            self._offset.setY(mouse_pos.y() - (rel_y * self.pixmap.height() * self._scale))
            
            self.update()
    
    def mousePressEvent(self, event):
        """Початок перетягування"""
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap and self._offset:
            self.dragging = True
            self.last_pan_point = event.position()
    
    def mouseMoveEvent(self, event):
        """Перетягування фото"""
        if self.dragging and self.last_pan_point and self._offset:
            delta = event.position() - self.last_pan_point
            self._offset.setX(self._offset.x() + delta.x())
            self._offset.setY(self._offset.y() + delta.y())
            self.last_pan_point = event.position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Завершення перетягування"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.last_pan_point = None
    
    def get_photo_params(self):
        """Повертає параметри фото для збереження"""
        return {
            'photo_path': self.photo_path,
            'photo_scale': self.photo_scale,
            'photo_offset_x': self.photo_offset_x,
            'photo_offset_y': self.photo_offset_y,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'saturation': self.saturation,
            'sharpness': self.sharpness
        }
    
    def set_photo_params(self, params):
        """Встановлює параметри фото"""
        self.photo_scale = params.get('photo_scale', 1.0)
        self.photo_offset_x = params.get('photo_offset_x', 0)
        self.photo_offset_y = params.get('photo_offset_y', 0)
        self.brightness = params.get('brightness', 0)
        self.contrast = params.get('contrast', 0)
        self.saturation = params.get('saturation', 0)
        self.sharpness = params.get('sharpness', 0)
        
        # Встановлюємо внутрішні параметри трансформації
        self._scale = self.photo_scale
        if self._offset is None:
            from PySide6.QtCore import QPointF
            self._offset = QPointF(self.photo_offset_x, self.photo_offset_y)
        else:
            self._offset.setX(self.photo_offset_x)
            self._offset.setY(self.photo_offset_y)
        
        if params.get('photo_path'):
            self.load_photo(params['photo_path'])
        else:
            self.update()
    
    def get_current_transform_params(self):
        """Повертає поточні параметри трансформації"""
        # Синхронізуємо внутрішні параметри з зовнішніми
        self.photo_scale = self._scale
        if self._offset:
            self.photo_offset_x = self._offset.x()
            self.photo_offset_y = self._offset.y()
        
        return {
            'photo_scale': self.photo_scale,
            'photo_offset_x': self.photo_offset_x,
            'photo_offset_y': self.photo_offset_y,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'saturation': self.saturation,
            'sharpness': self.sharpness
        }
    
    def _auto_fit_photo(self):
        """Автоматично підганяє фото під віджет"""
        if not self.pixmap:
            return
        
        widget_rect = self.rect()
        pixmap_rect = self.pixmap.rect()
        
        # Обчислюємо масштаб для вміщення зі збереженням пропорцій
        scale_x = widget_rect.width() / pixmap_rect.width()
        scale_y = widget_rect.height() / pixmap_rect.height()
        fit_scale = min(scale_x, scale_y) * 0.9  # Невеликий відступ
        
        # Встановлюємо масштаб та центруємо
        self._scale = fit_scale
        from PySide6.QtCore import QPointF
        center_x = (widget_rect.width() - pixmap_rect.width() * fit_scale) / 2
        center_y = (widget_rect.height() - pixmap_rect.height() * fit_scale) / 2
        self._offset = QPointF(center_x, center_y)
        
        self.update()
