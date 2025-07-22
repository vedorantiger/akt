# main.py
"""
Fitness CRM - Система управління клієнтами для тренерів
Автор: Денис
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qfluentwidgets import setTheme, Theme, setThemeColor
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from ui.main_window import MainWindow
from ui.styles import apply_theme, COLORS
from config.logger import fitness_logger, get_app_logger
from config import config
from config.database import test_connection

# Ініціалізуємо Rich Console для красивого виводу
console = Console()

# Отримуємо логгер для основної програми
app_logger = get_app_logger()


def main():
    """Головна функція запуску програми"""
    # Красивий стартовий банер
    console.print()
    console.print(Panel.fit(
        Text.from_markup(
            f"[bold blue]💪 {config.APP_NAME}[/bold blue]\n"
            f"[dim]Версія: {config.APP_VERSION}[/dim]\n"
            f"[dim]Автор: {config.APP_AUTHOR}[/dim]"
        ),
        title="[bold green]🚀 ЗАПУСК ПРОГРАМИ[/bold green]",
        border_style="bright_green"
    ))
    console.print()
    
    app_logger.info("🚀 Запуск Fitness CRM...")
    
    # Включаємо масштабування для високої роздільної здатності
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    # Примітка: AA_EnableHighDpiScaling та AA_UseHighDpiPixmaps застаріли в Qt6
    # High DPI підтримка увімкнена за замовчуванням
    
    # Створюємо додаток
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.APP_AUTHOR)
    app.setApplicationVersion(config.APP_VERSION)
    
    app_logger.info(f"📱 Додаток: {config.APP_NAME} v{config.APP_VERSION}")
    app_logger.info(f"👤 Автор: {config.APP_AUTHOR}")
    
    # Перевіряємо з'єднання з базою даних
    if not test_connection():
        app_logger.error("❌ Не вдалося підключитися до бази даних")
        return 1
    
    # Встановлюємо тему
    setTheme(Theme.LIGHT)
    setThemeColor(COLORS['primary'])
    app_logger.info("🎨 Встановлено світлу тему")
    
    # Застосовуємо кастомні стилі
    apply_theme(app)
    app_logger.info("✨ Застосовано кастомні стилі")
    
    # Створюємо і показуємо головне вікно
    try:
        window = MainWindow()
        window.resize(*config.WINDOW_SIZE)
        window.setWindowTitle(config.WINDOW_TITLE)
        window.show()
        app_logger.info("🪟 Головне вікно створено та показано")
        
        # Запускаємо додаток
        app_logger.info("▶️ Запуск головного циклу програми")
        result = app.exec()
        
        app_logger.info("🏁 Програма завершена")
        fitness_logger.log_shutdown()
        return result
        
    except Exception as e:
        app_logger.error(f"💥 Критична помилка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())