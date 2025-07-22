# ui/dialogs/photo_compare.py
"""Діалог для порівняння фотографій тестування"""
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from ui.widgets.photo_display import PhotoDisplayWidget, PhotoControlPanel


class PhotoCompareDialog(QDialog):
    """Діалог для порівняння фотографій тестування"""
    
    def __init__(self, photo_paths, parent=None):
        super().__init__(parent)
        self.photo_paths = photo_paths.copy()  # Копіюємо список
        self.photo_widgets = []
        self.control_panels = []
        self._current_drag_index = None
        
        self._init_ui()
        self._load_photos()
        self._setup_shortcuts()
    
    def _init_ui(self):
        """Створює інтерфейс діалогу"""
        self.setWindowTitle("📊 Порівняння фотографій тестування")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setModal(True)
        
        # Темна тема
        self.setStyleSheet("""
            QDialog {
                background-color: #1F2937;
            }
        """)
        
        # Основний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Область прокрутки для фотографій
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #1F2937;
            }
            QScrollBar:horizontal {
                background: #374151;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #6B7280;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #9CA3AF;
            }
            QScrollBar:vertical {
                background: #374151;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6B7280;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)
        main_layout.addWidget(scroll_area)
        
        # Віджет для вмісту
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: #1F2937;")
        scroll_area.setWidget(self.content_widget)
        
        # Layout для фотографій (горизонтальний)
        self.photos_layout = QHBoxLayout(self.content_widget)
        self.photos_layout.setContentsMargins(20, 20, 20, 20)
        self.photos_layout.setSpacing(20)
        
        # Нижня панель керування
        self._create_control_panel()
    
    def _create_control_panel(self):
        """Створює нижню панель керування"""
        control_frame = QFrame()
        control_frame.setFixedHeight(80)
        control_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border-top: 1px solid #374151;
            }
        """)
        
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(20, 15, 20, 15)
        control_layout.setSpacing(20)
        
        # Кнопка автоцентрування
        auto_center_btn = QPushButton("🎯 Автоцентрування")
        auto_center_btn.setFixedHeight(40)
        auto_center_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        auto_center_btn.clicked.connect(self._auto_center_all)
        control_layout.addWidget(auto_center_btn)
        
        # Підказка
        hint_label = QLabel("💡 Підказка: Утримуйте Ctrl і перетягніть фото, щоб поміняти їх місцями • Використовуйте коліщатко миші для зуму • Перетягуйте для переміщення")
        hint_label.setStyleSheet("""
            QLabel {
                color: #9CA3AF;
                font-size: 12px;
                font-style: italic;
            }
        """)
        control_layout.addWidget(hint_label)
        
        control_layout.addStretch()
        
        # Кнопка закриття
        close_btn = QPushButton("✖️ Закрити (Esc)")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #DC2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #B91C1C;
            }
        """)
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)
        
        # Додаємо панель до основного layout
        self.layout().addWidget(control_frame)
    
    def _load_photos(self):
        """Завантажує та відображає фотографії"""
        for i, photo_path in enumerate(self.photo_paths):
            # Створюємо колонку для кожного фото
            photo_column = QWidget()
            photo_column.setMinimumWidth(350)
            photo_column.setMaximumWidth(500)
            
            column_layout = QVBoxLayout(photo_column)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(10)
            
            # Рамка для фото
            photo_frame = QFrame()
            photo_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #374151;
                    border-radius: 12px;
                    background: #111827;
                }
            """)
            column_layout.addWidget(photo_frame)
            
            photo_frame_layout = QVBoxLayout(photo_frame)
            photo_frame_layout.setContentsMargins(10, 10, 10, 10)
            photo_frame_layout.setSpacing(8)
            
            # Заголовок фото
            photo_title = QLabel(f"Фото {i + 1}")
            photo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_title.setStyleSheet("""
                QLabel {
                    color: #F9FAFB;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 5px;
                    background: #374151;
                    border-radius: 6px;
                }
            """)
            photo_frame_layout.addWidget(photo_title)
            
            # Віджет фото
            photo_widget = PhotoDisplayWidget(photo_path, i, self)
            photo_widget.setMinimumSize(300, 300)
            photo_widget.drag_started.connect(self._on_drag_started)
            photo_widget.drop_accepted.connect(self._on_drop_accepted)
            photo_frame_layout.addWidget(photo_widget)
            
            # Панель керування фото
            control_panel = PhotoControlPanel(photo_widget)
            photo_frame_layout.addWidget(control_panel)
            
            # Додаємо до списків
            self.photo_widgets.append(photo_widget)
            self.control_panels.append(control_panel)
            
            # Додаємо колонку до layout
            self.photos_layout.addWidget(photo_column)
    
    def _setup_shortcuts(self):
        """Налаштовує гарячі клавіші"""
        # Esc для закриття
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.activated.connect(self.close)
        
        # Ctrl+A для автоцентрування
        center_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        center_shortcut.activated.connect(self._auto_center_all)
    
    def _on_drag_started(self, index):
        """Обробляє початок перетягування"""
        self._current_drag_index = index
    
    def _on_drop_accepted(self, from_index, to_index):
        """Обробляє завершення перетягування"""
        if from_index == to_index:
            return
        
        # Міняємо місцями шляхи до фотографій
        self.photo_paths[from_index], self.photo_paths[to_index] = \
            self.photo_paths[to_index], self.photo_paths[from_index]
        
        # Перезавантажуємо фотографії
        self.photo_widgets[from_index]._load_image()
        self.photo_widgets[to_index]._load_image()
        
        # Автоцентруємо
        self.photo_widgets[from_index]._auto_fit_photo()
        self.photo_widgets[to_index]._auto_fit_photo()
        
        # Скидаємо індекс перетягування
        self._current_drag_index = None
    
    def _auto_center_all(self):
        """Автоматично центрує всі фотографії"""
        for photo_widget in self.photo_widgets:
            photo_widget.center_photo()
    
    def closeEvent(self, event):
        """Обробляє закриття діалогу"""
        # Очищуємо ресурси
        for photo_widget in self.photo_widgets:
            photo_widget.deleteLater()
        
        for control_panel in self.control_panels:
            control_panel.deleteLater()
        
        super().closeEvent(event)


class PhotoCompareViewer(QWidget):
    """Простий переглядач для швидкого порівняння (без корекцій)"""
    
    def __init__(self, photo_paths, parent=None):
        super().__init__(parent)
        self.photo_paths = photo_paths
        self._init_ui()
        self._load_photos()
    
    def _init_ui(self):
        """Створює інтерфейс переглядача"""
        self.setWindowTitle("🔍 Швидке порівняння")
        self.resize(800, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Заголовок
        title_label = QLabel(f"Порівняння {len(self.photo_paths)} фотографій")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #111827;
                padding: 10px;
                background: #F3F4F6;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Віджет для фотографій
        photos_widget = QWidget()
        scroll_area.setWidget(photos_widget)
        
        # Layout для фотографій
        self.photos_layout = QHBoxLayout(photos_widget)
        self.photos_layout.setSpacing(15)
    
    def _load_photos(self):
        """Завантажує фотографії для перегляду"""
        from PySide6.QtGui import QPixmap
        
        for i, photo_path in enumerate(self.photo_paths):
            # Колонка для фото
            photo_column = QWidget()
            photo_column.setFixedWidth(250)
            
            column_layout = QVBoxLayout(photo_column)
            column_layout.setSpacing(8)
            
            # Заголовок
            title_label = QLabel(f"Фото {i + 1}")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #374151;
                    padding: 6px;
                    background: #E5E7EB;
                    border-radius: 6px;
                }
            """)
            column_layout.addWidget(title_label)
            
            # Фото
            photo_label = QLabel()
            photo_label.setFixedSize(240, 300)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #E5E7EB;
                    border-radius: 8px;
                    background: white;
                }
            """)
            
            if os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        238, 298,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    photo_label.setPixmap(scaled_pixmap)
                else:
                    photo_label.setText("📷\nПомилка завантаження")
            else:
                photo_label.setText("📷\nФото не знайдено")
            
            column_layout.addWidget(photo_label)
            column_layout.addStretch()
            
            self.photos_layout.addWidget(photo_column)
        
        self.photos_layout.addStretch()
