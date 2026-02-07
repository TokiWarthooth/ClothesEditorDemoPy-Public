#!/usr/bin/env python3
"""
Демонстрационная информация о Clothing Designer
"""

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           👗  CLOTHING DESIGNER  ✂️                       ║
    ║                                                           ║
    ║         Профессиональный редактор выкроек одежды          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_features():
    print("\n✨ НОВЫЕ ВОЗМОЖНОСТИ:")
    print("=" * 60)
    
    features = [
        ("📐 Библиотека шаблонов", "6 категорий готовых выкроек"),
        ("⚙️  Настраиваемые параметры", "Все размеры через слайдеры"),
        ("🎯 Точное позиционирование", "Сетка с привязкой"),
        ("🎨 Инструменты рисования", "7 профессиональных инструментов"),
        ("🌓 Темы оформления", "Светлая и темная темы"),
        ("💾 Управление проектами", "Сохранение и загрузка"),
    ]
    
    for feature, description in features:
        print(f"  {feature:30} {description}")

def print_templates():
    print("\n\n📚 ДОСТУПНЫЕ ШАБЛОНЫ:")
    print("=" * 60)
    
    templates = {
        "👔 Рукава (Sleeves)": [
            "• Базовый рукав с окатом",
            "  Параметры: ширина, длина, глубина оката"
        ],
        "👕 Воротники (Collars)": [
            "• Классический воротник",
            "  Параметры: ширина, высота, вырез горловины"
        ],
        "👖 Карманы (Pockets)": [
            "• Прямоугольный карман с закругленными углами",
            "  Параметры: ширина, высота, радиус углов"
        ],
        "👗 Юбки (Skirts)": [
            "• Панель юбки (передняя/задняя)",
            "  Параметры: талия, бедра, длина"
        ],
        "👖 Брюки (Trousers)": [
            "• Штанина",
            "  Параметры: талия, бедра, ширина низа, длина"
        ],
        "👚 Лиф (Bodice)": [
            "• Передняя часть лифа",
            "  Параметры: ширина, длина, плечи, вырез"
        ]
    }
    
    for category, details in templates.items():
        print(f"\n{category}")
        for detail in details:
            print(f"  {detail}")

def print_quick_start():
    print("\n\n🚀 БЫСТРЫЙ СТАРТ:")
    print("=" * 60)
    
    steps = [
        "1. Запустите: python3 main.py",
        "2. Выберите 'New Project'",
        "3. Нажмите кнопку 'Pattern' в панели инструментов",
        "4. Выберите категорию и шаблон",
        "5. Настройте параметры слайдерами",
        "6. Нажмите 'Add to Canvas'",
        "7. Кликните на холсте для размещения",
        "8. Перетаскивайте шаблоны для изменения позиции"
    ]
    
    for step in steps:
        print(f"  {step}")

def print_hotkeys():
    print("\n\n⌨️  ГОРЯЧИЕ КЛАВИШИ:")
    print("=" * 60)
    
    hotkeys = [
        ("Ctrl+N", "Новый проект"),
        ("Ctrl+O", "Открыть проект"),
        ("Ctrl+S", "Сохранить проект"),
        ("Ctrl+Q", "Выход"),
    ]
    
    for key, action in hotkeys:
        print(f"  {key:15} {action}")

def print_docs():
    print("\n\n📖 ДОКУМЕНТАЦИЯ:")
    print("=" * 60)
    
    docs = [
        ("README.md", "Основная информация о проекте"),
        ("QUICK_START_RU.md", "Быстрый старт на русском"),
        ("PATTERN_TEMPLATES_GUIDE.md", "Руководство по шаблонам"),
        ("FEATURES.md", "Полный список функций"),
    ]
    
    for doc, description in docs:
        print(f"  {doc:30} {description}")

def print_footer():
    print("\n" + "=" * 60)
    print("  Создано с ❤️  для дизайнеров одежды и портных")
    print("=" * 60)
    print()

def main():
    print_banner()
    print_features()
    print_templates()
    print_quick_start()
    print_hotkeys()
    print_docs()
    print_footer()

if __name__ == "__main__":
    main()
