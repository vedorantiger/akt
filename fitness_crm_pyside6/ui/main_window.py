# ui/main_window.py
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QGridLayout, QScrollArea
from PySide6.QtGui import QResizeEvent
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, setTheme, Theme, 
    SearchLineEdit, PrimaryPushButton, SegmentedWidget,
    StrongBodyLabel, InfoBar, InfoBarPosition
)
from qfluentwidgets import FluentIcon as FIF
import qtawesome as qta  # Додаємо QtAwesome для іконок
from ui.widgets.photo_card import PhotoCard
from ui.widgets.list_item import ListItemWidget
from ui.dialogs.edit_client.main_dialog import EditClientDialog
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
        self.current_view = "grid"  # Поточний режим перегляду: "grid" або "list"
        
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
        
        # Кнопка додавання
        self.add_btn = PrimaryPushButton("➕ Додати клієнта")
        self.add_btn.setFixedHeight(40)
        self.add_btn.clicked.connect(self.add_client)
        
        # Підпис для перемикача виду
        view_label = StrongBodyLabel("Вигляд:")
        view_label.setStyleSheet("color: #374151; font-weight: 600; font-size: 14px;")
        
        # Перемикач виду
        self.view_toggle = SegmentedWidget()
        self.view_toggle.addItem("grid", "🔳", lambda: self._switch_to_grid_view())
        self.view_toggle.addItem("list", "📄", lambda: self._switch_to_list_view())
        self.view_toggle.setCurrentItem("grid")
        self.view_toggle.setFixedHeight(40)
        
        control_layout.addWidget(self.search_input)
        control_layout.addStretch()
        control_layout.addWidget(view_label)
        control_layout.addWidget(self.view_toggle)
        control_layout.addWidget(self.add_btn)
        
        layout.addWidget(control_panel)
        
        # Створюємо основний контейнер з прокруткою
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Контейнер для карток
        self.cards_container = QWidget()
        self.cards_container.setObjectName("cardsContainer")
        self.cards_container.setStyleSheet("""
            QWidget#cardsContainer {
                background-color: #f8f9fa;
            }
        """)
        
        # Грід лейаут для карток
        self.cards_grid_layout = QGridLayout(self.cards_container)
        self.cards_grid_layout.setSpacing(UI_SETTINGS['card_spacing'])
        self.cards_grid_layout.setContentsMargins(
            UI_SETTINGS['min_margin'], 
            UI_SETTINGS['min_margin'],
            UI_SETTINGS['min_margin'], 
            UI_SETTINGS['min_margin']
        )
        
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
    
    def add_test_clients(self):
        """Додати тестових клієнтів"""
        # Завантажуємо клієнтів з файлів
        self._load_clients_from_files()
        self._update_display()
    
    def _load_clients_from_files(self):
        """Завантажує клієнтів з JSON файлів"""
        import os
        import json
        
        clients_dir = "data/clients"
        if not os.path.exists(clients_dir):
            print(f"📁 Директорія {clients_dir} не існує")
            return
        
        # Очищаємо попередні картки
        self.client_cards.clear()
        
        files = os.listdir(clients_dir)
        print(f"📂 Знайдено файлів в {clients_dir}: {files}")
        
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(clients_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        client_data = json.load(f)
                    
                    print(f"✅ Завантажено клієнта: {client_data.get('full_name', 'Невідомий')} (ID: {client_data.get('id')})")
                    
                    # Створюємо картку клієнта
                    card = PhotoCard(client_data, self)
                    card.clicked.connect(lambda cid=client_data.get('id'): self.open_client(cid))
                    card.edit_requested.connect(lambda cid=client_data.get('id'): self.edit_client(cid))
                    card.delete_requested.connect(lambda cid=client_data.get('id'): self.delete_client(cid))
                    card.swap_requested.connect(self._handle_card_swap)
                    
                    self.client_cards.append(card)
                    
                except Exception as e:
                    print(f"❌ Помилка завантаження клієнта з файлу {filename}: {e}")
        
        print(f"🔢 Загалом завантажено клієнтів: {len(self.client_cards)}")
    
    def _update_display(self):
        """Оновлення відображення карток або списку"""
        print(f"🔄 Оновлення відображення. Карток для відображення: {len(self.client_cards)}, Режим: {self.current_view}")
        
        # Очищаємо лейаут
        self._clear_layout()
        
        # Отримуємо розміри контейнера
        container_width = self.cards_container.width()
        if container_width <= 100:  # Захист від некоректних розмірів
            print(f"⚠️ Контейнер ще не готовий, ширина: {container_width}")
            return
        
        if self.current_view == "grid":
            self._display_grid_view(container_width)
        else:
            self._display_list_view(container_width)
    
    def _display_grid_view(self, container_width):
        """Відображення у вигляді сітки карток"""
        # Розраховуємо кількість колонок
        total_spacing = UI_SETTINGS['min_margin'] * 2
        available_width = container_width - total_spacing
        card_with_spacing = UI_SETTINGS['card_width'] + UI_SETTINGS['card_spacing']
        columns = max(1, min(available_width // card_with_spacing, UI_SETTINGS['max_columns']))
        
        print(f"📐 Розміщення сітки: {columns} колонок, ширина контейнера: {container_width}")
        
        # Розставляємо картки
        for i, card in enumerate(self.client_cards):
            row = i // columns
            col = i % columns
            self.cards_grid_layout.addWidget(card, row, col)
            self._active_widgets.append(card)
            print(f"  📍 Картка {i+1}: позиція ({row}, {col}) | Розмір: {card.size()} | Видимість: {card.isVisible()}")
        
        # Показуємо всі картки ПІСЛЯ додавання в лейаут
        for card in self.client_cards:
            card.show()
            card.setVisible(True)
            
        # Додаємо stretch для вирівнювання
        self.cards_grid_layout.setColumnStretch(columns, 1)
        
    def _display_list_view(self, container_width):
        """Відображення у вигляді списку"""
        print(f"📝 Розміщення списку: ширина контейнера: {container_width}")
        
        # Створюємо список елементів
        for i, client_data in enumerate([card.client_data for card in self.client_cards]):
            # Створюємо елемент списку
            list_item = ListItemWidget(client_data, self)
            list_item.clicked.connect(lambda cid=client_data.get('id'): self.open_client(cid))
            list_item.edit_requested.connect(lambda cid=client_data.get('id'): self.edit_client(cid))
            list_item.delete_requested.connect(lambda cid=client_data.get('id'): self.delete_client(cid))
            
            # Встановлюємо ширину списку на повну ширину контейнера мінус відступи
            list_item.setMinimumWidth(container_width - UI_SETTINGS['min_margin'] * 2)
            
            # Додаємо в одну колонку (список) - зліва
            self.cards_grid_layout.addWidget(list_item, i, 0, Qt.AlignLeft | Qt.AlignTop)
            list_item.show()
            list_item.setVisible(True)
            self._active_widgets.append(list_item)
            
            print(f"  📝 Список-елемент {i+1}: рядок {i} | Ширина: {list_item.minimumWidth()} | Висота: {list_item.height()}")
        
        # НЕ додаємо stretch - список буде зліва        # Показуємо контейнер та скрол
        self.cards_container.show()
        self.scroll_area.show()
        
        print(f"✅ Відображення оновлено. Активних віджетів: {len(self._active_widgets)}")
    
    def _clear_layout(self):
        """Очищення лейауту"""
        print(f"🧹 Очищення лейауту. Поточних активних віджетів: {len(self._active_widgets)}")
        
        # Видаляємо всі віджети з лейауту
        while self.cards_grid_layout.count():
            child = self.cards_grid_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Очищаємо список активних віджетів
        self._active_widgets.clear()
        
        print("✅ Лейаут очищено")
    
    def resizeEvent(self, event: QResizeEvent):
        """Обробка зміни розміру вікна"""
        super().resizeEvent(event)
        self.resize_timer.start()  # Перезапускаємо таймер
    
    def _switch_to_grid_view(self):
        """Перемикання на вид сітки"""
        print("🔳 Перемикання на вид сітки")
        self.current_view = "grid"
        self._update_display()
        
        InfoBar.success(
            title='Вигляд змінено',
            content="Перемикання на вид сітки",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
    
    def _switch_to_list_view(self):
        """Перемикання на вид списку"""
        print("📝 Перемикання на вид списку")
        self.current_view = "list"
        self._update_display()
        
        InfoBar.info(
            title='Вигляд змінено',
            content="Перемикання на вид списку",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
        # TODO: Реалізувати вид списку
    
    def _add_client_card(self, client_data):
        """Додати нову картку клієнта"""
        card = PhotoCard(client_data, self)
        card.clicked.connect(lambda: self.open_client(client_data.get('id')))
        card.edit_requested.connect(lambda: self.edit_client(client_data.get('id')))
        card.delete_requested.connect(lambda: self.delete_client(client_data.get('id')))
        card.swap_requested.connect(self._handle_card_swap)
        
        self.client_cards.append(card)
        self._update_display()
    
    def add_client(self):
        """Додати нового клієнта"""
        dialog = EditClientDialog(parent=self)
        dialog.client_saved.connect(self._on_client_saved)
        
        if dialog.exec() == QDialog.Accepted:
            pass
    
    def _on_client_saved(self, client_data):
        """Обробка збереження нового клієнта"""
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
        # Шукаємо MainWindow в ієрархії батьківських об'єктів
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'edit_client'):
            main_window = main_window.parent()
        
        if main_window and hasattr(main_window, 'edit_client'):
            main_window.edit_client(client_id)
    
    def delete_client(self, client_id: str):
        """Видалити клієнта - переадресовуємо до MainWindow"""
        # Шукаємо MainWindow в ієрархії батьківських об'єктів
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'delete_client'):
            main_window = main_window.parent()
            
        if main_window and hasattr(main_window, 'delete_client'):
            main_window.delete_client(client_id)
    
    def _handle_card_swap(self, source_id: str, target_id: str):
        """Обробляє зміну порядку карток - переадресовуємо до MainWindow"""
        # Шукаємо MainWindow в ієрархії батьківських об'єктів
        main_window = self.parent()
        while main_window and not hasattr(main_window, '_handle_card_swap'):
            main_window = main_window.parent()
            
        if main_window and hasattr(main_window, '_handle_card_swap'):
            main_window._handle_card_swap(source_id, target_id)


class MainWindow(FluentWindow):
    """Головне вікно програми"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness CRM - Система управління клієнтами")
        self.resize(1200, 800)
        
        # Встановлюємо світлу тему
        setTheme(Theme.LIGHT)
        
        # Збільшуємо розмір іконок навігації
        self.navigationInterface.setExpandWidth(300)  # Розширюємо ширину панелі
        
        # Створюємо сторінки
        self.clients_page = ClientsPage(self)
        
        # Додаємо сторінки до навігації
        self.addSubInterface(
            self.clients_page, 
            FIF.PEOPLE, 
            "Клієнти"
        )
        self.addSubInterface(
            self._create_placeholder_page("Тренування"), 
            FIF.BASKETBALL, 
            "Тренування"
        )
        self.addSubInterface(
            self._create_placeholder_page("Харчування"), 
            FIF.CALORIES, 
            "Харчування"
        )
        self.addSubInterface(
            self._create_placeholder_page("Аналітика"), 
            qta.icon('fa5s.chart-pie'),  # Використовуємо QtAwesome іконку
            "Аналітика"
        )
        self.addSubInterface(
            self._create_placeholder_page("Налаштування"), 
            FIF.SETTING, 
            "Налаштування", 
            position=NavigationItemPosition.BOTTOM
        )
        
        # Додаємо корзину
        self.trash_page = self._create_trash_page()
        self.addSubInterface(
            self.trash_page,
            FIF.DELETE,
            "Корзина", 
            position=NavigationItemPosition.BOTTOM
        )
        
        # Встановлюємо стартову сторінку
        self.navigationInterface.setCurrentItem("Клієнти")
        
        # Збільшуємо іконки навігації через стилі
        self._setup_navigation_styles()
    
    def _setup_navigation_styles(self):
        """Налаштовує стилі навігації для збільшення іконок"""
        navigation_style = """
        NavigationInterface {
            background-color: #f8f9fa;
        }
        
        NavigationTreeWidget {
            font-size: 18px;
            border: none;
            background-color: transparent;
        }
        
        NavigationTreeWidget::item {
            height: 60px;
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px 8px;
        }
        
        NavigationTreeWidget::item:selected {
            background-color: rgba(0, 120, 212, 0.1);
        }
        
        NavigationTreeWidget::item:hover {
            background-color: rgba(0, 120, 212, 0.05);
        }
        
        /* Збільшуємо іконки */
        NavigationTreeWidget QLabel {
            font-size: 32px;
            color: #333;
        }
        """
        
        self.navigationInterface.setStyleSheet(navigation_style)
    
    def _create_placeholder_page(self, title):
        """Створює заглушку для сторінки"""
        page = QWidget()
        page.setObjectName(f"{title.lower().replace(' ', '_')}_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        label = StrongBodyLabel(f"{title} - в розробці")
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
        title_label = StrongBodyLabel("🗑️ Корзина")
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
        clients_page = self.stackedWidget.widget(0)  # Перша сторінка - це сторінка клієнтів
        
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
                        except Exception:
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
        # Отримуємо сторінку клієнтів
        clients_page = self.stackedWidget.widget(0)  # Перша сторінка - це сторінка клієнтів
        
        if hasattr(clients_page, 'client_cards'):
            # Знайдемо картку клієнта і оновимо її
            client_id = client_data.get('id')
            for card in clients_page.client_cards:
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
                        except Exception:
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
                clients_page = self.stackedWidget.widget(0)
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
            clients_page = self.stackedWidget.widget(0)
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
