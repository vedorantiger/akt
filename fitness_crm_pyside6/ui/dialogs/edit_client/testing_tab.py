# ui/dialogs/edit_client/testing_tab.py
"""Вкладка тестування клієнта"""
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                               QPushButton, QScrollArea, QGridLayout, QLabel, QFileDialog)
from PySide6.QtCore import Qt
from qfluentwidgets import MessageBox
from ui.styles import COLORS
from ui.widgets.testing_card import TestingPhotoCard, TestingTextCard
from ui.dialogs.testing_photo_info_dialog import TestingPhotoInfoDialog, TestingTextInfoDialog
from ui.dialogs.photo_compare import PhotoCompareDialog


class TestingTab(QWidget):
    """Вкладка тестування клієнта"""
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data or {}
        
        # Якщо немає ID (новий клієнт), створюємо тимчасовий
        if self.client_data.get('id'):
            self.client_id = self.client_data.get('id')
        else:
            import uuid
            self.client_id = f"temp_{str(uuid.uuid4())[:8]}"
            
        self.testing_photos = []  # Список словників з інформацією про фото
        self.text_blocks = []  # Список текстових блоків
        self.selected_photos = []  # Список вибраних фото для порівняння
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
        
        # ===== ФОТОГРАФІЇ ТЕСТУВАННЯ =====
        photos_group = QGroupBox("📸 Фото для тестування")
        photos_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(photos_group)
        
        photos_layout = QVBoxLayout(photos_group)
        photos_layout.setContentsMargins(20, 25, 20, 20)
        photos_layout.setSpacing(15)
        
        # Кнопки керування фото
        buttons_layout = QHBoxLayout()
        
        self.add_photos_btn = QPushButton("➕ Додати фото тестування")
        self.add_photos_btn.setFixedSize(200, 40)
        self.add_photos_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: #2563eb;
            }}
        """)
        self.add_photos_btn.clicked.connect(self._add_photos)
        
        self.compare_photos_btn = QPushButton("� Порівняти вибрані")
        self.compare_photos_btn.setFixedSize(180, 40)
        self.compare_photos_btn.setEnabled(False)
        self.compare_photos_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['secondary']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: #7C3AED;
            }}
            QPushButton:disabled {{
                background: #9CA3AF;
                color: #6B7280;
            }}
        """)
        self.compare_photos_btn.clicked.connect(self._compare_photos)
        
        buttons_layout.addWidget(self.add_photos_btn)
        buttons_layout.addWidget(self.compare_photos_btn)
        buttons_layout.addStretch()
        
        photos_layout.addLayout(buttons_layout)
        
        # Статистика фото
        stats_layout = QHBoxLayout()
        
        self.photos_count_label = QLabel("📷 Фото: 0")
        self.photos_count_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #6B7280;
                font-weight: 500;
            }
        """)
        
        self.selected_count_label = QLabel("✅ Вибрано: 0")
        self.selected_count_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #059669;
                font-weight: 500;
            }
        """)
        
        stats_layout.addWidget(self.photos_count_label)
        stats_layout.addWidget(self.selected_count_label)
        stats_layout.addStretch()
        
        photos_layout.addLayout(stats_layout)
        
        # Область для карток фото
        self.photos_scroll = QScrollArea()
        self.photos_scroll.setWidgetResizable(True)
        self.photos_scroll.setMinimumHeight(300)
        self.photos_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #F9FAFB;
            }
        """)
        photos_layout.addWidget(self.photos_scroll)
        
        self.photos_grid_widget = QWidget()
        self.photos_scroll.setWidget(self.photos_grid_widget)
        
        self.photos_grid = QGridLayout(self.photos_grid_widget)
        self.photos_grid.setSpacing(15)
        self.photos_grid.setContentsMargins(15, 15, 15, 15)
        
        # ===== ТЕКСТОВІ БЛОКИ ТЕСТУВАННЯ =====
        text_group = QGroupBox("� Текстові блоки тестування")
        text_group.setStyleSheet(self._get_group_style())
        content_layout.addWidget(text_group)
        
        text_layout = QVBoxLayout(text_group)
        text_layout.setContentsMargins(20, 25, 20, 20)
        text_layout.setSpacing(15)
        
        # Кнопка додавання текстових блоків
        text_buttons_layout = QHBoxLayout()
        
        self.add_text_btn = QPushButton("➕ Додати текстовий блок")
        self.add_text_btn.setFixedSize(200, 40)
        self.add_text_btn.setStyleSheet("""
            QPushButton {
                background: #8B5CF6;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #7C3AED;
            }
        """)
        self.add_text_btn.clicked.connect(self._add_text_block)
        
        text_buttons_layout.addWidget(self.add_text_btn)
        text_buttons_layout.addStretch()
        
        text_layout.addLayout(text_buttons_layout)
        
        # Область для текстових карток
        self.text_scroll = QScrollArea()
        self.text_scroll.setWidgetResizable(True)
        self.text_scroll.setMinimumHeight(200)
        self.text_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #F9FAFB;
            }
        """)
        text_layout.addWidget(self.text_scroll)
        
        self.text_blocks_widget = QWidget()
        self.text_scroll.setWidget(self.text_blocks_widget)
        
        self.text_blocks_layout = QVBoxLayout(self.text_blocks_widget)
        self.text_blocks_layout.setSpacing(10)
        self.text_blocks_layout.setContentsMargins(15, 15, 15, 15)
        
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
    
    def _get_client_testing_folder(self):
        """Повертає шлях до папки тестування клієнта"""
        if not self.client_id:
            return None
        
        client_folder = os.path.join("data", "clients", self.client_id)
        testing_folder = os.path.join(client_folder, "photos", "testing")
        
        # Створюємо папку якщо не існує
        os.makedirs(testing_folder, exist_ok=True)
        return testing_folder
    
    def _add_photos(self):
        """Додає фото тестування"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Оберіть фото тестування",
            "",
            "Зображення (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if not file_paths:
            return
        
        testing_folder = self._get_client_testing_folder()
        if not testing_folder:
            MessageBox.warning(
                title="Помилка",
                content="Не вдалося створити папку для фото тестування",
                parent=self
            )
            return
        
        for file_path in file_paths:
            # Відкриваємо діалог для введення інформації
            info_dialog = TestingPhotoInfoDialog(self)
            if info_dialog.exec() == info_dialog.Accepted:
                date_taken, description = info_dialog.get_info()
                
                # Копіюємо файл до папки клієнта
                filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"testing_{timestamp}_{filename}"
                new_path = os.path.join(testing_folder, new_filename)
                
                try:
                    shutil.copy2(file_path, new_path)
                    
                    # Додаємо інформацію про фото
                    photo_info = {
                        'path': new_path,
                        'date_taken': date_taken,
                        'description': description,
                        'timestamp': timestamp
                    }
                    self.testing_photos.append(photo_info)
                    
                except Exception as e:
                    MessageBox.warning(
                        title="Помилка",
                        content=f"Не вдалося скопіювати файл: {str(e)}",
                        parent=self
                    )
        
        self._update_photos_display()
    
    def _add_text_block(self):
        """Додає текстовий блок"""
        info_dialog = TestingTextInfoDialog(parent=self)
        if info_dialog.exec() == info_dialog.Accepted:
            date_created, text_content = info_dialog.get_content()
            
            text_block = {
                'date_created': date_created,
                'text_content': text_content,
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
            }
            self.text_blocks.append(text_block)
            self._update_text_blocks_display()
    
    def _update_photos_display(self):
        """Оновлює відображення фото"""
        # Очищуємо попередній layout
        for i in reversed(range(self.photos_grid.count())):
            item = self.photos_grid.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Додаємо картки фото
        for i, photo_info in enumerate(self.testing_photos):
            photo_card = TestingPhotoCard(
                photo_info['path'],
                photo_info['date_taken'],
                photo_info['description']
            )
            
            # Підключаємо сигнали
            photo_card.selection_changed.connect(self._on_photo_selection_changed)
            photo_card.delete_requested.connect(self._delete_photo)
            photo_card.edit_requested.connect(self._edit_photo_info)
            
            # Розміщуємо в сітці (3 колонки)
            row = i // 3
            col = i % 3
            self.photos_grid.addWidget(photo_card, row, col)
        
        # Оновлюємо статистику
        self._update_stats()
    
    def _update_text_blocks_display(self):
        """Оновлює відображення текстових блоків"""
        # Очищуємо попередній layout
        for i in reversed(range(self.text_blocks_layout.count())):
            item = self.text_blocks_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Додаємо картки текстових блоків
        for i, text_block in enumerate(self.text_blocks):
            text_card = TestingTextCard(
                i,
                text_block['date_created'],
                text_block['text_content']
            )
            
            # Підключаємо сигнали
            text_card.delete_requested.connect(self._delete_text_block)
            text_card.edit_requested.connect(self._edit_text_block)
            
            self.text_blocks_layout.addWidget(text_card)
        
        # Додаємо розтягувач в кінці
        self.text_blocks_layout.addStretch()
    
    def _on_photo_selection_changed(self, selected, photo_path):
        """Обробляє зміну вибору фото"""
        if selected:
            if photo_path not in self.selected_photos:
                self.selected_photos.append(photo_path)
        else:
            if photo_path in self.selected_photos:
                self.selected_photos.remove(photo_path)
        
        self._update_stats()
    
    def _update_stats(self):
        """Оновлює статистику"""
        total_photos = len(self.testing_photos)
        selected_count = len(self.selected_photos)
        
        self.photos_count_label.setText(f"📷 Фото: {total_photos}")
        self.selected_count_label.setText(f"✅ Вибрано: {selected_count}")
        
        # Включаємо/вимикаємо кнопку порівняння
        self.compare_photos_btn.setEnabled(2 <= selected_count <= 6)
    
    def _compare_photos(self):
        """Відкриває діалог порівняння фото"""
        if len(self.selected_photos) < 2:
            MessageBox.warning(
                title="Недостатньо фото",
                content="Для порівняння потрібно вибрати мінімум 2 фотографії",
                parent=self
            )
            return
        
        if len(self.selected_photos) > 6:
            MessageBox.warning(
                title="Забагато фото",
                content="Для порівняння можна вибрати максимум 6 фотографій",
                parent=self
            )
            return
        
        # Відкриваємо діалог порівняння
        compare_dialog = PhotoCompareDialog(self.selected_photos, self)
        compare_dialog.exec()
    
    def _delete_photo(self, photo_path):
        """Видаляє фото"""
        result = MessageBox.question(
            title="Підтвердження видалення",
            content="Ви впевнені, що хочете видалити це фото?",
            parent=self
        )
        
        if result == 1:  # Yes
            # Видаляємо з списку
            self.testing_photos = [p for p in self.testing_photos if p['path'] != photo_path]
            
            # Видаляємо з вибраних
            if photo_path in self.selected_photos:
                self.selected_photos.remove(photo_path)
            
            # Видаляємо файл
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except Exception as e:
                print(f"Помилка видалення файлу: {e}")
            
            self._update_photos_display()
    
    def _edit_photo_info(self, photo_path):
        """Редагує інформацію про фото"""
        # Знаходимо фото в списку
        photo_info = None
        for p in self.testing_photos:
            if p['path'] == photo_path:
                photo_info = p
                break
        
        if not photo_info:
            return
        
        # Відкриваємо діалог редагування
        info_dialog = TestingPhotoInfoDialog(self)
        
        # Встановлюємо поточні дані
        try:
            from PySide6.QtCore import QDate
            date_parts = photo_info['date_taken'].split('.')
            if len(date_parts) == 3:
                day, month, year = map(int, date_parts)
                info_dialog.date_edit.setDate(QDate(year, month, day))
        except:
            pass
        
        info_dialog.description_edit.setText(photo_info['description'])
        
        if info_dialog.exec() == info_dialog.Accepted:
            date_taken, description = info_dialog.get_info()
            photo_info['date_taken'] = date_taken
            photo_info['description'] = description
            self._update_photos_display()
    
    def _delete_text_block(self, index):
        """Видаляє текстовий блок"""
        if 0 <= index < len(self.text_blocks):
            result = MessageBox.question(
                title="Підтвердження видалення",
                content="Ви впевнені, що хочете видалити цей текстовий блок?",
                parent=self
            )
            
            if result == 1:  # Yes
                del self.text_blocks[index]
                self._update_text_blocks_display()
    
    def _edit_text_block(self, index):
        """Редагує текстовий блок"""
        if 0 <= index < len(self.text_blocks):
            text_block = self.text_blocks[index]
            
            info_dialog = TestingTextInfoDialog(
                text_block['date_created'],
                text_block['text_content'],
                self
            )
            
            if info_dialog.exec() == info_dialog.Accepted:
                date_created, text_content = info_dialog.get_content()
                text_block['date_created'] = date_created
                text_block['text_content'] = text_content
                self._update_text_blocks_display()
    
    def _load_data(self):
        """Завантажує дані клієнта"""
        if not self.client_data:
            return
        
        # Завантажуємо фото тестування
        self.testing_photos = self.client_data.get('testing_photos', [])
        self._update_photos_display()
        
        # Завантажуємо текстові блоки
        self.text_blocks = self.client_data.get('testing_text_blocks', [])
        self._update_text_blocks_display()
    
    def get_data(self):
        """Повертає дані вкладки"""
        return {
            'testing_photos': self.testing_photos,
            'testing_text_blocks': self.text_blocks
        }
