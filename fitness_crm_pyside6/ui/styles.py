# ui/styles.py
"""Стилі для Fitness CRM"""

# Кольорова палітра (світла бізнес-тема)
COLORS = {
    # Основні кольори
    'primary': '#0078D4',        # Microsoft Blue
    'primary_hover': '#106EBE',
    'primary_pressed': '#005A9E',
    
    # Вторинні кольори
    'secondary': '#8B5CF6',      # Фіолетовий
    'info': '#06B6D4',           # Блакитний
    'success': '#10B981',        # Зелений
    
    # Акцентні кольори
    'accent': '#107C10',         # Зелений для успіху
    'warning': '#FFB900',        # Жовтий для попереджень
    'error': '#D83B01',          # Червоний для помилок
    
    # Фонові кольори
    'background': '#FAFAFA',     # Основний фон
    'surface': '#FFFFFF',        # Поверхня карток
    'sidebar': '#FFFFFF',        # Бокова панель
    
    # Текстові кольори
    'text_primary': '#323130',   # Основний текст
    'text_secondary': '#605E5C', # Вторинний текст
    'text_disabled': '#A19F9D',  # Неактивний текст
    
    # Лінії та розділювачі
    'border': '#EDEBE9',         # Границі
    'divider': '#E1DFDD',        # Розділювачі
    
    # Тіні
    'shadow': 'rgba(0, 0, 0, 0.133)',
}

# Стилі для головного вікна
MAIN_WINDOW_STYLE = f"""
    MainWindow {{
        background-color: {COLORS['background']};
    }}
"""

# Стилі для навігаційної панелі
NAVIGATION_STYLE = f"""
    NavigationInterface {{
        background-color: {COLORS['sidebar']};
        border-right: 1px solid {COLORS['border']};
    }}
    
    NavigationTreeWidget {{
        background-color: transparent;
        border: none;
        outline: none;
    }}
"""

# Стилі для карток клієнтів
CLIENT_CARD_STYLE = f"""
    ClientCard {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    }}
    
    ClientCard:hover {{
        border: 1px solid {COLORS['primary']};
        box-shadow: 0 4px 12px {COLORS['shadow']};
    }}
"""

# Стилі для кнопок
BUTTON_STYLES = f"""
    PrimaryPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
    }}
    
    PrimaryPushButton:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    
    PrimaryPushButton:pressed {{
        background-color: {COLORS['primary_pressed']};
    }}
"""

# Стилі для пошукового поля
SEARCH_STYLE = f"""
    SearchLineEdit {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
    }}
    
    SearchLineEdit:focus {{
        border: 1px solid {COLORS['primary']};
    }}
"""

# Об'єднаний стиль для всієї програми
APP_STYLE = f"""
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 14px;
        color: {COLORS['text_primary']};
    }}
    
    {MAIN_WINDOW_STYLE}
    {NAVIGATION_STYLE}
    {CLIENT_CARD_STYLE}
    {BUTTON_STYLES}
    {SEARCH_STYLE}
    
    /* Скролбар */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['divider']};
    }}
    
    /* Лейбли */
    StrongBodyLabel {{
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    
    BodyLabel {{
        color: {COLORS['text_secondary']};
    }}
"""

# Функція для застосування теми
def apply_theme(app):
    """Застосовує тему до програми"""
    app.setStyleSheet(APP_STYLE)
    
    # Додаткові налаштування для Windows
    if hasattr(app, 'setStyle'):
        app.setStyle('Fusion')

# Експорт стилів для використання в інших модулях
__all__ = ['COLORS', 'APP_STYLE', 'apply_theme']