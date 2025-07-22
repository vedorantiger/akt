# ui/widgets/photo_display.py
"""Віджет для відображення та корекції фотографій"""
import os
from PIL import Image, ImageEnhance
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSlider, QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QPointF
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QPainter, QTransform


# Мінімальний стиль для слайдерів
MINI_SLIDER_STYLE = """
QSlider::groove:horizontal {
    border: 1px solid #CCCCCC;
    height: 6px;
    background: #F0F0F0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #4A90E2;
    border: 1px solid #357ABD;
    width: 14px;
    height: 14px;
    border-radius: 7px;
    margin: -4px 0;
}
QSlider::handle:horizontal:hover {
    background: #357ABD;
}
QSlider::sub-page:horizontal {
    background: #4A90E2;
    border-radius: 3px;
}
"""


class PhotoDisplayWidget(QLabel):
    """Віджет для відображення фото з зумом, панорамуванням та корекцією"""
    
    # Сигнали
    drag_started = Signal(int)  # індекс фото
    drop_accepted = Signal(int, int)  # з_індексу, в_індекс
    
    def __init__(self, photo_path, index=0, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.index = index
        self.parent_widget = parent
        
        # Параметри відображення
        self._scale = 1.0
        self._offset = QPointF(0, 0)
        self._brightness = 0  # -100 до 100
        self._contrast = 100  # 0 до 200
        self._saturation = 100  # 0 до 200
        self._sharpness = 100  # 0 до 400
        
        # Оригінальне зображення
        self._original_image = None
        self._current_pixmap = None
        
        # Перетягування
        self._dragging = False
        self._drag_start_pos = QPointF()
        self._is_drag_drop_mode = False
        
        # Таймер для корекції
        self._adjustment_timer = QTimer()
        self._adjustment_timer.setSingleShot(True)
        self._adjustment_timer.timeout.connect(self._apply_adjustments)
        
        self._init_ui()
        self._load_image()
    
    def _init_ui(self):
        """Налаштовує віджет"""
        self.setMinimumSize(300, 300)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background: #F9FAFB;
            }
        """)
        
        # Включаємо обробку подій миші
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
    
    def _load_image(self):
        """Завантажує оригінальне зображення"""
        if not os.path.exists(self.photo_path):
            self.setText("📷\nФото не знайдено")
            return
        
        try:
            self._original_image = Image.open(self.photo_path).convert('RGB')
            self._auto_fit_photo()
        except Exception as e:
            self.setText(f"📷\nПомилка: {str(e)}")
    
    def _auto_fit_photo(self):
        """Автоматично вписує фото в віджет"""
        if not self._original_image:
            return
        
        # Розраховуємо оптимальний масштаб
        widget_size = self.size()
        img_size = self._original_image.size
        
        scale_x = (widget_size.width() - 20) / img_size[0]
        scale_y = (widget_size.height() - 20) / img_size[1]
        self._scale = min(scale_x, scale_y, 1.0)  # Не збільшуємо більше оригіналу
        
        # Центруємо зображення
        self._offset = QPointF(0, 0)
        
        self._apply_adjustments()
    
    def _apply_adjustments(self):
        """Застосовує всі корекції до зображення"""
        if not self._original_image:
            return
        
        # Копіюємо оригінальне зображення
        img = self._original_image.copy()
        
        # Застосовуємо корекції
        if self._brightness != 0:
            brightness_factor = 1.0 + (self._brightness / 100.0)
            img = ImageEnhance.Brightness(img).enhance(brightness_factor)
        
        if self._contrast != 100:
            contrast_factor = self._contrast / 100.0
            img = ImageEnhance.Contrast(img).enhance(contrast_factor)
        
        if self._saturation != 100:
            saturation_factor = self._saturation / 100.0
            img = ImageEnhance.Color(img).enhance(saturation_factor)
        
        if self._sharpness != 100:
            sharpness_factor = self._sharpness / 100.0
            img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)
        
        # Конвертуємо в QPixmap
        img_qt = img.convert('RGB')
        width, height = img_qt.size
        img_data = img_qt.tobytes('raw', 'RGB')
        
        from PySide6.QtGui import QImage
        qimg = QImage(img_data, width, height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # Застосовуємо масштаб та зміщення
        if self._scale != 1.0 or self._offset != QPointF(0, 0):
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * self._scale),
                int(pixmap.height() * self._scale),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Створюємо фінальний pixmap з врахуванням зміщення
            final_pixmap = QPixmap(self.size())
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(final_pixmap)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # Розраховуємо позицію для центрування + зміщення
            x = (self.width() - scaled_pixmap.width()) // 2 + int(self._offset.x())
            y = (self.height() - scaled_pixmap.height()) // 2 + int(self._offset.y())
            
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            self._current_pixmap = final_pixmap
        else:
            self._current_pixmap = pixmap
        
        self.setPixmap(self._current_pixmap)
    
    def wheelEvent(self, event: QWheelEvent):
        """Обробляє прокрутку миші для зуму"""
        if not self._original_image:
            return
        
        # Зум
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        
        old_scale = self._scale
        self._scale *= zoom_factor
        self._scale = max(0.1, min(5.0, self._scale))  # Обмежуємо масштаб
        
        # Корекція зміщення для зуму відносно позиції миші
        if old_scale != self._scale:
            mouse_pos = event.position()
            widget_center = QPointF(self.width() / 2, self.height() / 2)
            
            # Відносна позиція миші від центру
            relative_pos = mouse_pos - widget_center
            
            # Корекція зміщення
            scale_ratio = self._scale / old_scale
            self._offset = (self._offset - relative_pos) * scale_ratio + relative_pos
        
        self._apply_adjustments()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Обробляє натискання миші"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Перевіряємо, чи затиснуто Ctrl для drag-and-drop
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._is_drag_drop_mode = True
                self.drag_started.emit(self.index)
                self.setStyleSheet("""
                    QLabel {
                        border: 3px dashed #0EA5E9;
                        border-radius: 8px;
                        background: rgba(14, 165, 233, 0.1);
                        opacity: 0.7;
                    }
                """)
            else:
                # Звичайне перетягування для панорамування
                self._dragging = True
                self._drag_start_pos = event.position()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Обробляє рух миші"""
        if self._dragging and not self._is_drag_drop_mode:
            # Панорамування
            delta = event.position() - self._drag_start_pos
            self._offset += delta
            self._drag_start_pos = event.position()
            self._apply_adjustments()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обробляє відпускання миші"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            
            if self._is_drag_drop_mode:
                self._is_drag_drop_mode = False
                # Повертаємо нормальний стиль
                self.setStyleSheet("""
                    QLabel {
                        border: 2px solid #E5E7EB;
                        border-radius: 8px;
                        background: #F9FAFB;
                    }
                """)
    
    def dragEnterEvent(self, event):
        """Обробляє вхід в зону drag-and-drop"""
        if hasattr(self.parent_widget, '_current_drag_index'):
            if self.parent_widget._current_drag_index != self.index:
                self.setStyleSheet("""
                    QLabel {
                        border: 3px dashed #10B981;
                        border-radius: 8px;
                        background: rgba(16, 185, 129, 0.1);
                    }
                """)
                event.accept()
    
    def dragLeaveEvent(self, event):
        """Обробляє вихід з зони drag-and-drop"""
        if not self._is_drag_drop_mode:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #E5E7EB;
                    border-radius: 8px;
                    background: #F9FAFB;
                }
            """)
    
    def dropEvent(self, event):
        """Обробляє drop"""
        if hasattr(self.parent_widget, '_current_drag_index'):
            from_index = self.parent_widget._current_drag_index
            to_index = self.index
            if from_index != to_index:
                self.drop_accepted.emit(from_index, to_index)
        
        # Повертаємо нормальний стиль
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background: #F9FAFB;
            }
        """)
    
    def get_current_transform_params(self):
        """Повертає поточні параметри трансформації"""
        return {
            'photo_scale': self._scale,
            'photo_offset_x': self._offset.x(),
            'photo_offset_y': self._offset.y(),
            'brightness': self._brightness,
            'contrast': self._contrast,
            'saturation': self._saturation,
            'sharpness': self._sharpness
        }
    
    def set_photo_params(self, params):
        """Встановлює параметри фото"""
        self._scale = params.get('photo_scale', 1.0)
        self._offset = QPointF(
            params.get('photo_offset_x', 0),
            params.get('photo_offset_y', 0)
        )
        self._brightness = params.get('brightness', 0)
        self._contrast = params.get('contrast', 100)
        self._saturation = params.get('saturation', 100)
        self._sharpness = params.get('sharpness', 100)
        self._apply_adjustments()
    
    def set_brightness(self, value):
        """Встановлює яскравість"""
        self._brightness = value
        self._adjustment_timer.start(50)  # Затримка для плавності
    
    def set_contrast(self, value):
        """Встановлює контраст"""
        self._contrast = value
        self._adjustment_timer.start(50)
    
    def set_saturation(self, value):
        """Встановлює насиченість"""
        self._saturation = value
        self._adjustment_timer.start(50)
    
    def set_sharpness(self, value):
        """Встановлює різкість"""
        self._sharpness = value
        self._adjustment_timer.start(50)
    
    def reset_adjustments(self):
        """Скидає всі корекції"""
        self._brightness = 0
        self._contrast = 100
        self._saturation = 100
        self._sharpness = 100
        self._auto_fit_photo()
    
    def center_photo(self):
        """Центрує фото"""
        self._auto_fit_photo()


class PhotoControlPanel(QWidget):
    """Панель керування фото з слайдерами корекції"""
    
    def __init__(self, photo_display_widget, parent=None):
        super().__init__(parent)
        self.photo_widget = photo_display_widget
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Створює інтерфейс панелі"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Панель з темним фоном
        panel_frame = QFrame()
        panel_frame.setStyleSheet("""
            QFrame {
                background: #374151;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        main_layout.addWidget(panel_frame)
        
        panel_layout = QVBoxLayout(panel_frame)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(8)
        
        # Слайдери корекції
        sliders_layout = QVBoxLayout()
        sliders_layout.setSpacing(4)
        
        # Яскравість
        self.brightness_slider = self._create_slider("☀️ Яскравість", -100, 100, 0)
        sliders_layout.addLayout(self.brightness_slider)
        
        # Контраст
        self.contrast_slider = self._create_slider("◐ Контраст", 0, 200, 100)
        sliders_layout.addLayout(self.contrast_slider)
        
        # Насиченість
        self.saturation_slider = self._create_slider("🎨 Насиченість", 0, 200, 100)
        sliders_layout.addLayout(self.saturation_slider)
        
        # Різкість
        self.sharpness_slider = self._create_slider("🔪 Різкість", 0, 400, 100)
        sliders_layout.addLayout(self.sharpness_slider)
        
        panel_layout.addLayout(sliders_layout)
        
        # Кнопки дій
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        reset_btn = QPushButton("🔄")
        reset_btn.setFixedSize(30, 24)
        reset_btn.setToolTip("Скинути корекції")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #6B7280;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #9CA3AF;
            }
        """)
        reset_btn.clicked.connect(self._reset_adjustments)
        
        center_btn = QPushButton("🎯")
        center_btn.setFixedSize(30, 24)
        center_btn.setToolTip("Центрувати")
        center_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        center_btn.clicked.connect(self.photo_widget.center_photo)
        
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(center_btn)
        buttons_layout.addStretch()
        
        panel_layout.addLayout(buttons_layout)
    
    def _create_slider(self, label_text, min_val, max_val, default_val):
        """Створює слайдер з підписом"""
        layout = QHBoxLayout()
        layout.setSpacing(6)
        
        # Підпис
        label = QLabel(label_text)
        label.setFixedWidth(90)
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        layout.addWidget(label)
        
        # Слайдер
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.setStyleSheet(MINI_SLIDER_STYLE)
        layout.addWidget(slider)
        
        # Значення
        value_label = QLabel(str(default_val))
        value_label.setFixedWidth(35)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10px;
                background: #4B5563;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        layout.addWidget(value_label)
        
        # Зберігаємо посилання на value_label в слайдері
        slider.value_label = value_label
        
        return layout
    
    def _connect_signals(self):
        """Підключає сигнали слайдерів"""
        # Яскравість
        brightness_slider = self.brightness_slider.itemAt(1).widget()
        brightness_slider.valueChanged.connect(self.photo_widget.set_brightness)
        brightness_slider.valueChanged.connect(lambda v: brightness_slider.value_label.setText(str(v)))
        
        # Контраст
        contrast_slider = self.contrast_slider.itemAt(1).widget()
        contrast_slider.valueChanged.connect(self.photo_widget.set_contrast)
        contrast_slider.valueChanged.connect(lambda v: contrast_slider.value_label.setText(str(v)))
        
        # Насиченість
        saturation_slider = self.saturation_slider.itemAt(1).widget()
        saturation_slider.valueChanged.connect(self.photo_widget.set_saturation)
        saturation_slider.valueChanged.connect(lambda v: saturation_slider.value_label.setText(str(v)))
        
        # Різкість
        sharpness_slider = self.sharpness_slider.itemAt(1).widget()
        sharpness_slider.valueChanged.connect(self.photo_widget.set_sharpness)
        sharpness_slider.valueChanged.connect(lambda v: sharpness_slider.value_label.setText(str(v)))
    
    def _reset_adjustments(self):
        """Скидає всі корекції"""
        # Скидаємо слайдери
        self.brightness_slider.itemAt(1).widget().setValue(0)
        self.contrast_slider.itemAt(1).widget().setValue(100)
        self.saturation_slider.itemAt(1).widget().setValue(100)
        self.sharpness_slider.itemAt(1).widget().setValue(100)
        
        # Скидаємо в photo widget
        self.photo_widget.reset_adjustments()
