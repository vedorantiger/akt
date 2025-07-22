# ui/main_window.py
from PySide6.QtCore import Qt, QSize, Signal, QTimer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QGridLayout
from PySide6.QtGui import QIcon, QResizeEvent
from qfluentwidgets import (
    FluentWindow, NavigationInterface, NavigationItemPosition,
    setTheme, Theme, FluentIcon, NavigationTreeWidget,
    SearchLineEdit, PrimaryPushButton, SegmentedWidget,
    CardWidget, BodyLabel, StrongBodyLabel, ImageLabel,
    TransparentToolButton, InfoBar, InfoBarPosition,
    FlowLayout, SingleDirectionScrollArea
)
from qfluentwidgets import FluentIcon as FIF
from ui.widgets.photo_card import PhotoCard
from ui.dialogs.edit_client import EditClientDialog
import sys


# Константи для UI налаштувань
UI_SETTINGS = {
    'card_width': 320,      # Ширина картки
    'card_spacing': 25,     # Відстань між картками
    'min_margin': 40,       # Мінімальні відступи
    'max_columns': 5        # Максимальна кількість колонок
}


class ClientsPage(QWidget):
    """Сторінка клієнтів"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("clientsPage")
        self.client_cards = []  # Список всіх карток клієнтів
        self._active_widgets = []  # Активні віджети
        
        # Створюємо таймер для оптимізації resize
        self.resize_timer = QTimer(self)
        self.resize_timer.setInterval(100)  # Затримка 100 мс
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._update_display)
        
        self._init_ui()
        self.add_test_clients()
        
    def _init_ui(self):
        """Ініціалізація інтерфейсу"""
        # Основний layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Панель управління
        control_panel = QWidget()
        control_panel.setFixedHeight(60)
        control_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
            }
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 10, 20, 10)
        control_layout.setSpacing(15)
        
        # Пошук
        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("🔍 Пошук клієнтів...")
        self.search_input.setFixedWidth(400)
        self.search_input.setFixedHeight(40)
        
        # Кнопка додати
        self.add_btn = PrimaryPushButton("➕ Додати клієнта", self, FIF.ADD)
        self.add_btn.setFixedHeight(40)
        self.add_btn.setFixedWidth(160)
        self.add_btn.clicked.connect(self.add_client)
        
        # Перемикач виду
        self.view_switcher = SegmentedWidget(self)
        self.view_switcher.setFixedHeight(40)
        self.view_switcher.addItem("list", "Список", self.switch_to_list_view)
        self.view_switcher.addItem("cards", "Картки", self.switch_to_cards_view)
        self.view_switcher.setCurrentItem("cards")
        
        control_layout.addWidget(self.search_input)
        control_layout.addStretch()
        control_layout.addWidget(self.add_btn)
        control_layout.addWidget(self.view_switcher)
        
        # Область прокрутки для клієнтів
        self.scroll_area = SingleDirectionScrollArea(self, Qt.Vertical)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Покращуємо плавність прокрутки
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setSingleStep(20)  # Менші кроки для плавності
        scrollbar.setPageStep(100)   # Швидше прокручування сторінками
        
        # Вмикаємо плавну прокрутку
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Контейнер для карток (основний віджет для адаптивної сітки)
        self._grid_scroll_widget = QWidget()
        self._grid_scroll_widget.setStyleSheet("background-color: transparent;")
        
        # Адаптивний грід лейаут
        self.cards_grid_layout = QGridLayout(self._grid_scroll_widget)
        self.cards_grid_layout.setSpacing(UI_SETTINGS['card_spacing'])  # Відстань між картками
        self.cards_grid_layout.setContentsMargins(
            UI_SETTINGS['min_margin'], 30, 
            UI_SETTINGS['min_margin'], 30
        )  # Початкові відступи
        self.cards_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self._grid_scroll_widget)
        
        layout.addWidget(control_panel)
        layout.addWidget(self.scroll_area)
    
    def _clear_layout(self, layout):
        """Очищує layout від всіх віджетів"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
    
    def _calculate_adaptive_layout(self):
        """Розраховує адаптивний layout для карток"""
        # Отримуємо поточну ширину viewport
        viewport_width = self.scroll_area.viewport().width()
        
        # Розраховуємо оптимальну кількість колонок
        card_total_width = UI_SETTINGS['card_width'] + UI_SETTINGS['card_spacing']
        columns = max(1, min(UI_SETTINGS['max_columns'], 
                            (viewport_width - 2 * UI_SETTINGS['min_margin']) // card_total_width))
        
        # Розраховуємо відступи для симетричного центрування
        total_cards_width = (columns * UI_SETTINGS['card_width'] + 
                            (columns - 1) * UI_SETTINGS['card_spacing'])
        side_margin = max(UI_SETTINGS['min_margin'], (viewport_width - total_cards_width) // 2)
        
        return columns, side_margin
    
    def _update_display(self):
        """Оновлює відображення карток з адаптивним layout"""
        if not self.client_cards:
            return
        
        # Очищуємо попередній layout
        self._clear_layout(self.cards_grid_layout)
        
        # Розраховуємо адаптивний layout
        columns, side_margin = self._calculate_adaptive_layout()
        
        # Встановлюємо нові відступи для центрування
        self.cards_grid_layout.setContentsMargins(side_margin, 30, side_margin, 30)
        
        # Розміщуємо картки в сітці
        for i, card in enumerate(self.client_cards):
            row = i // columns
            col = i % columns
            self.cards_grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignCenter)
            card.show()
    
    def resizeEvent(self, event: QResizeEvent):
        """Обробка зміни розміру вікна"""
        super().resizeEvent(event)
        # Запускаємо таймер для оптимізації
        if hasattr(self, 'resize_timer'):
            self.resize_timer.start()
    
    def add_test_clients(self):
        """Завантажуємо збережених клієнтів з файлів"""
        # Зберігаємо картки для адаптивності
        self.client_cards = []
        
        # Завантажуємо клієнтів з файлів JSON
        self._load_clients_from_files()
        
        # Оновлюємо відображення
        self._update_display()
    
    def _load_clients_from_files(self):
        """Завантажує клієнтів з файлів JSON"""
        import os
        import json
        
        clients_dir = "data/clients"
        if not os.path.exists(clients_dir):
            return
        
        # Перебираємо всі JSON файли в папці клієнтів
        for filename in os.listdir(clients_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(clients_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        client_data = json.load(f)
                    
                    # Створюємо картку клієнта
                    card = PhotoCard(client_data)
                    card.clicked.connect(self.open_client)
                    card.edit_requested.connect(self.edit_client)
                    card.delete_requested.connect(self.delete_client)
                    card.swap_requested.connect(self._handle_card_swap)
                    self.client_cards.append(card)
                    
                except Exception as e:
                    print(f"❌ Помилка завантаження клієнта {filename}: {e}")
    
    def _add_client_card(self, client_data):
        """Додає нову картку клієнта до інтерфейсу"""
        # Створюємо нову картку
        card = PhotoCard(client_data)
        card.clicked.connect(self.open_client)
        card.edit_requested.connect(self.edit_client)
        card.delete_requested.connect(self.delete_client)
        card.swap_requested.connect(self._handle_card_swap)
        
        # Додаємо до списку
        self.client_cards.append(card)
        
        # Оновлюємо відображення
        self._update_display()
    
    def add_client(self):
        """Додати нового клієнта"""
        dialog = EditClientDialog(parent=self)
        dialog.client_saved.connect(self._on_client_saved)
        
        if dialog.exec():
            # Діалог закрито з результатом "Прийнято"
            pass
    
    def _on_client_saved(self, client_data):
        """Обробка збереження клієнта"""
        # Формуємо повне ім'я
        first_name = client_data.get('first_name', '')
        surname = client_data.get('surname', '')
        full_name = f"{first_name} {surname}".strip() or 'Невідомий'
        
        InfoBar.success(
            title='Успіх',
            content=f"Клієнта '{full_name}' успішно збережено",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
        # Додаємо нову картку клієнта до інтерфейсу
        self._add_client_card(client_data)
    
    def open_client(self, client_id: str):
        """Відкрити сторінку клієнта"""
        InfoBar.info(
            title='Інформація',
            content=f"Відкриття клієнта ID: {client_id}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def edit_client(self, client_id: str):
        """Редагувати клієнта - переадресовуємо до MainWindow"""
        if self.parent():
            self.parent().edit_client(client_id)
    
    def delete_client(self, client_id: str):
        """Видалити клієнта - переадресовуємо до MainWindow"""
        if self.parent():
            self.parent().delete_client(client_id)
    
    def _handle_card_swap(self, source_id: str, target_id: str):
        """Обробляє зміну порядку карток - переадресовуємо до MainWindow"""
        if self.parent():
            self.parent()._handle_card_swap(source_id, target_id)
    
    def switch_to_list_view(self):
        """Перемикання на вид списку"""
        InfoBar.info(
            title='Вид',
            content="Перемикання на вид списку",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
        # TODO: Реалізувати вид списку
    
    def switch_to_cards_view(self):
        """Перемикання на вид карток"""
        InfoBar.info(
            title='Вид',
            content="Перемикання на вид карток",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
        # TODO: Реалізувати логіку перемикання виду


class MainWindow(FluentWindow):
    """Головне вікно програми"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness CRM - Система управління клієнтами")
        self.resize(1200, 800)
        
        # Встановлюємо світлу тему
        setTheme(Theme.LIGHT)
        
        # Створюємо сторінки
        self.clients_page = ClientsPage(self)
        self.schedule_page = self._create_placeholder_page("Розклад")
        self.reports_page = self._create_placeholder_page("Звіти")
        self.settings_page = self._create_placeholder_page("Налаштування")
        self.trash_page = self._create_trash_page()
        
        # Ініціалізуємо навігацію
        self.init_navigation()
    
    def edit_client(self, client_id: str):
        """Редагувати клієнта"""
        try:
            # Знайдемо дані клієнта по ID
            client_data = None
            import os
            import json
            
            clients_dir = "data/clients"
            if os.path.exists(clients_dir):
                for filename in os.listdir(clients_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(clients_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('id') == client_id:
                                client_data = data
                                break
                        except:
                            continue
            
            if not client_data:
                InfoBar.error(
                    title='Помилка',
                    content=f"Клієнта з ID {client_id} не знайдено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # Відкриваємо діалог редагування
            dialog = EditClientDialog(client_data=client_data, parent=self)
            dialog.client_saved.connect(self._on_client_updated)
            
            if dialog.exec() == QDialog.Accepted:
                # Діалог закрито з результатом "Прийнято"
                pass
                
        except Exception as e:
            InfoBar.error(
                title='Помилка',
                content=f"Помилка при редагуванні клієнта: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def _on_client_updated(self, client_data):
        """Обробка оновлення клієнта"""
        # Отримуємо сторінку клієнтів напряму
        if hasattr(self.clients_page, 'client_cards'):
            # Знайдемо картку клієнта і оновимо її
            client_id = client_data.get('id')
            for i, card in enumerate(self.clients_page.client_cards):
                if hasattr(card, 'client_data') and card.client_data.get('id') == client_id:
                    # Оновлюємо дані картки
                    card.client_data = client_data
                    # Повністю перезавантажуємо картку
                    card.updateCardData(client_data)
                    break
        
        InfoBar.success(
            title='Збережено',
            content=f"Клієнта '{client_data.get('full_name', 'Невідомий')}' успішно оновлено",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
        
        # Стилізація
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
            }
            NavigationInterface {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
        """)
    
    def init_navigation(self):
        """Налаштування навігації"""
        # Додаємо сторінки до навігації
        self.addSubInterface(self.clients_page, FIF.PEOPLE, "Клієнти")
        self.addSubInterface(self.schedule_page, FIF.CALENDAR, "Розклад")
        self.addSubInterface(self.reports_page, FIF.DOCUMENT, "Звіти")
        
        # Нижні елементи навігації
        self.addSubInterface(
            self.settings_page, 
            FIF.SETTING, 
            "Налаштування",
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.trash_page,
            FIF.DELETE,
            "Корзина", 
            position=NavigationItemPosition.BOTTOM
        )
        
        # Встановлюємо стартову сторінку
        self.navigationInterface.setCurrentItem("Клієнти")
    
    def _create_placeholder_page(self, title):
        """Створює заглушку для сторінки"""
        page = QWidget()
        page.setObjectName(f"{title.lower().replace(' ', '_')}_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        label = StrongBodyLabel(f"{title} - в розробці", page)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        return page
    
    def _create_trash_page(self):
        """Створює сторінку корзини"""
        page = QWidget()
        page.setObjectName("trash_page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title_label = StrongBodyLabel("🗑️ Корзина", page)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Кнопка відкриття повного діалогу корзини
        open_trash_btn = PrimaryPushButton("📂 Відкрити корзину")
        open_trash_btn.setFixedSize(200, 40)
        open_trash_btn.clicked.connect(self._open_trash_dialog)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(open_trash_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return page
    
    def _open_trash_dialog(self):
        """Відкриває діалог корзини"""
        from ui.dialogs.trash_dialog import TrashDialog
        dialog = TrashDialog(self)
        dialog.client_restored.connect(self._on_client_restored)
        dialog.exec()
    
    def _on_client_restored(self):
        """Обробка відновлення клієнта з корзини"""
        # Отримуємо сторінку клієнтів
        clients_page = self.stack_widget.widget(0)  # Перша сторінка - це сторінка клієнтів
        
        if hasattr(clients_page, 'client_cards'):
            # Перезавантажуємо всіх клієнтів
            clients_page.client_cards.clear()
            clients_page._load_clients_from_files()
            clients_page._update_display()
        
        InfoBar.success(
            title='Оновлено',
            content="Список клієнтів оновлено після відновлення",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def edit_client(self, client_id: str):
        """Редагувати клієнта"""
        try:
            import os
            import json
            
            # Знайдемо дані клієнта по ID
            client_data = None
            clients_dir = "data/clients"
            
            if os.path.exists(clients_dir):
                for filename in os.listdir(clients_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(clients_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('id') == client_id:
                                client_data = data
                                break
                        except:
                            continue
            
            if not client_data:
                InfoBar.error(
                    title='Помилка',
                    content=f"Клієнта з ID {client_id} не знайдено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # Відкриваємо діалог редагування
            from ui.dialogs.edit_client.main_dialog import EditClientDialog
            dialog = EditClientDialog(client_data=client_data, parent=self)
            dialog.client_saved.connect(self._on_client_updated)
            
            if dialog.exec() == QDialog.Accepted:
                # Діалог закрито з результатом "Прийнято"
                pass
                
        except Exception as e:
            InfoBar.error(
                title='Помилка',
                content=f"Помилка при редагуванні клієнта: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def _on_client_updated(self, client_data):
        """Обробка оновлення клієнта"""
        # Отримуємо сторінку клієнтів
        clients_page = self.stack_widget.widget(0)  # Перша сторінка - це сторінка клієнтів
        
        if hasattr(clients_page, 'client_cards'):
            # Знайдемо картку клієнта і оновимо її
            client_id = client_data.get('id')
            for i, card in enumerate(clients_page.client_cards):
                if hasattr(card, 'client_data') and card.client_data.get('id') == client_id:
                    # Оновлюємо дані картки
                    card.client_data = client_data
                    # Повністю перезавантажуємо картку з новими даними
                    if hasattr(card, 'updateCardData'):
                        card.updateCardData(client_data)
                    break
        
        InfoBar.success(
            title='Збережено',
            content=f"Клієнта '{client_data.get('full_name', 'Невідомий')}' успішно оновлено",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def delete_client(self, client_id: str):
        """Видалити клієнта"""
        try:
            import os
            import json
            import shutil
            from datetime import datetime
            from qfluentwidgets import MessageBox
            
            # Знайдемо дані клієнта
            client_data = None
            clients_dir = "data/clients"
            filepath = None
            
            if os.path.exists(clients_dir):
                for filename in os.listdir(clients_dir):
                    if filename.endswith('.json'):
                        temp_filepath = os.path.join(clients_dir, filename)
                        try:
                            with open(temp_filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('id') == client_id:
                                client_data = data
                                filepath = temp_filepath
                                break
                        except:
                            continue
            
            if not client_data:
                InfoBar.error(
                    title='Помилка',
                    content=f"Клієнта з ID {client_id} не знайдено",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # Підтвердження видалення
            first_name = client_data.get('first_name', '')
            surname = client_data.get('surname', '')
            display_name = f"{first_name} {surname}".strip() or 'Невідомий'
            
            result = MessageBox(
                title="🗑️ Підтвердження видалення",
                content=f"Ви дійсно хочете видалити клієнта '{display_name}'?\n\nЦя дія незворотня!",
                parent=self
            ).exec()
            
            if result == 1:  # 1 означає "Так" в QFluentWidgets
                # Переміщуємо клієнта в корзину
                if filepath and os.path.exists(filepath):
                    # Створюємо папку корзини
                    trash_dir = "data/trash"
                    os.makedirs(trash_dir, exist_ok=True)
                    
                    # Створюємо унікальну папку для клієнта в корзині
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = "".join(c for c in display_name if c.isalnum() or c in ' -_').strip().replace(' ', '_')[:20]
                    client_trash_dir = os.path.join(trash_dir, f"{safe_name}_{timestamp}")
                    os.makedirs(client_trash_dir, exist_ok=True)
                    
                    # Переміщуємо JSON файл
                    filename = os.path.basename(filepath)
                    trash_filepath = os.path.join(client_trash_dir, filename)
                    shutil.move(filepath, trash_filepath)
                
                # Видаляємо картку з інтерфейсу
                clients_page = self.stack_widget.widget(0)
                if hasattr(clients_page, 'client_cards'):
                    for i, card in enumerate(clients_page.client_cards):
                        if card.client_data.get('id') == client_id:
                            # Видаляємо з лейауту
                            clients_page.cards_grid_layout.removeWidget(card)
                            card.setParent(None)
                            # Видаляємо зі списку
                            clients_page.client_cards.pop(i)
                            break
                    
                    # Оновлюємо розкладку
                    clients_page._update_display()
                
                InfoBar.success(
                    title='Успіх',
                    content=f"Клієнта '{display_name}' переміщено в корзину",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title='Помилка',
                content=f"Помилка при видаленні клієнта: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def _handle_card_swap(self, source_id: str, target_id: str):
        """Обробляє зміну порядку карток"""
        try:
            clients_page = self.stack_widget.widget(0)
            if hasattr(clients_page, 'client_cards'):
                # Знаходимо індекси карток
                source_index = -1
                target_index = -1
                
                for i, card in enumerate(clients_page.client_cards):
                    if card.client_data.get('id') == source_id:
                        source_index = i
                    elif card.client_data.get('id') == target_id:
                        target_index = i
                
                if source_index != -1 and target_index != -1:
                    # Міняємо місцями картки в списку
                    clients_page.client_cards[source_index], clients_page.client_cards[target_index] = \
                        clients_page.client_cards[target_index], clients_page.client_cards[source_index]
                    
                    # Оновлюємо розкладку
                    clients_page._update_display()
                    
                    InfoBar.success(
                        title='Успіх',
                        content="Порядок клієнтів змінено",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                    
        except Exception as e:
            InfoBar.error(
                title='Помилка',
                content=f"Помилка при зміні порядку: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
