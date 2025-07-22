Fitness CRM (PySide6)
Планується створення десктопного фітнес-провідника — сучасної CRM‑системи для тренерів, яка працює на Windows, написана мовою Python (PySide6).
🔧 Основні можливості:
📋 Створення, редагування та управління клієнтами
📸 Збереження та порівняння фото‑прогресу
📈 Відслідковування фізичних параметрів і цілей
🧾 Генерація звітів (PDF, Word)
📊 Аналітика з графіками (Plotly, Pandas)
🧠  АІ‑помічник 

Проєкт орієнтований на локальну роботу, з використанням SQLite як бази даних.

структура проекту:

fitness_crm_pyside6/
├── 📄 main.py                          # Запуск програми
├── 📄 .pre-commit-config.yaml          # Автоматичне форматування коду перед комітом.
├── 📄 requirements.txt                 # Залежності
├── 📄 project_structure.txt            # Ваша довідкова структура (цей файл)
│
├── 📁 config/                          # Конфігураційні файли
│   ├── 📄 config.py                        # Налаштування
│   ├── 📄 database.py                      # База даних
│   ├── 📄 logger.py                        # Логування
│   └── 📄 .pre-commit-config.yaml          # Автоматичне форматування коду перед комітом.
│   
├── 📁 models/                          # Моделі даних
│   ├── 📄 __init__.py
│   ├── 📄 client_list.py               # Клас для керування списком або картмами
│   └── 📄 client.py                    # Модель клієнта
│
├── 📁 ui/                              # Інтерфейс
│   ├── 📄 __init__.py
│   ├── 📄 main_window.py               # Головне вікно
│   ├── 📄 styles.py                    # Стилі
│   │
│   ├── 📁 dialogs/                     # Діалогові вікна
│   │   ├── 📄 __init__.py
│   │   ├── 📄 client_page.py           # Сторінка клієнта
│   │   ├── 📄 photo_viewer.py          # Перегляд фото
│   │   ├── 📄 photo_compare.py         # Порівняння фото
│   │   ├── 📄 trash_dialog.py          # Корзина
│   │   │
│   │   └── 📁 edit_client/             # 🎯 покищо 8 ВКЛАДОК 
│   │       ├── 📄 __init__.py
│   │       ├── 📄 main_dialog.py       # Основний діалог
│   │       ├── 📄 basic_tab.py         # 1️⃣ Основні дані
│   │       ├── 📄 physical_tab.py      # 2️⃣ Фізичні параметри
│   │       ├── 📄 health_tab.py        # 3️⃣ Здоров'я
│   │       ├── 📄 lifestyle_tab.py     # 4️⃣ Спосіб життя
│   │       ├── 📄 goals_tab.py         # 5️⃣ Цілі та плани
│   │       ├── 📄 measurements_tab.py  # 6️⃣ Поточні заміри
│   │       ├── 📄 testing_tab.py       # 7️⃣ Тестування
│   │       └── 📄 ai_tab.py            # 8️⃣ Персональний АІ
│   │
│   └── 📁 widgets/                     # Віджети
│       ├── 📄 __init__.py
│       ├── 📄 photo_card.py            # Картка клієнта
│       ├── 📄 list_item.py             # Елемент списку
│       ├── 📄 photo_display.py         # Відображення фото
│       ├── 📄 testing_card.py          # Картка тестування
│       ├── 📄 document_card.py         # Картка документа
│       └── 📄 toast.py                 # Спливаючі повідомлення
│
├── 📁 analytics/                       # 📊 Аналітика (НОВЕ!)
│   ├── 📄 __init__.py
│   ├── 📄 charts.py                    # Графіки Plotly
│   ├── 📄 data_processor.py            # Обробка даних Pandas
│   └── 📄 reports.py                   # Звіти PDF
│
├── 📁 utils/                           # Утиліти
│   ├── 📄 __init__.py
│   ├── 📄 helpers.py                   # Допоміжні функції
│   ├── 📄 validators.py                # Валідатори
│   ├── 📄 file_utils.py                # Утиліти для роботи з файлами та папками
│   ├── 📄 image_processor.py           # Утиліти для обробки зображень (зміна розміру, обрізка)
│   ├── 📄 calculations.py              # Розрахунки
│   └── 📄 ai_helper.py                 # АІ помічник
│
├── 📁 data/                            # 📂 Дані програми
│   ├── 📁 clients/                     # Дані клієнтів
│   │   ├── 📁 [Прізвище_Ім'я_ID]/     # Папки клієнтів зунікальни ID при створенні
│   │   │   ├── 📄 client_data.json     # JSON дані
│   │   │   ├── 📁 photos/              # Фото клієнта
│   │   │   ├── 📁 documents/           # Документи клієнта
│   │   │   ├── 📁 testing/             # Відео Клієнта 
│   │   │   ├── 📁 other/               # папка для різного
│   │   │   └── 📁 reports/             # Звіти клієнта
│   │   └── ...
│   ├── 📁 backup/                      # Резервні копії
│   │   └── 📄 backup_YYYY_MM_DD.zip   # Автобекапи
│   ├── 📁 trash/                       # Корзина
│   │   └── 📁 [видалені_файли]/       # Видалені елементи
│   └── 📁 templates/                   # 📋 Шаблони (PDF/Word)
│       ├── 📄 client_card.docx         # Картка клієнта
│       ├── 📄 diet_plan.docx           # План дієти
│       ├── 📄 progress_report.pdf      # Звіт прогресу
│       └── 📄 training_plan.pdf        # План тренувань
│
├── 📁 logs/                            # 📝 Логи програми
│   ├── 📄 app_YYYY_MM.log             # Основні логи
│   ├── 📄 database_YYYY_MM.log        # Логи БД
│   ├── 📄 ui_YYYY_MM.log              # Логи інтерфейсу
│   └── 📄 errors_YYYY_MM.log          # Логи помилок
│
└── 📁 database/                       # 🗃️ SQLite база даних (ORM: SQLModel + SQLAlchemy)
    └── 📄 fitness_crm.db              # Фізичний .db-файл, створений через SQLModel