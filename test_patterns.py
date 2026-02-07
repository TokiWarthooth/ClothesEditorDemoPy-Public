#!/usr/bin/env python3
"""
Скрипт для тестирования библиотеки шаблонов выкроек
"""

from app.pattern_templates import PatternLibrary

def test_pattern_library():
    """Тестирует библиотеку шаблонов"""
    print("=" * 60)
    print("Testing Pattern Library")
    print("=" * 60)
    
    library = PatternLibrary()
    
    # Проверяем категории
    categories = library.get_categories()
    print(f"\n✓ Found {len(categories)} categories:")
    for cat in categories:
        print(f"  - {cat}")
    
    # Проверяем шаблоны в каждой категории
    print("\n" + "=" * 60)
    print("Templates by Category:")
    print("=" * 60)
    
    total_templates = 0
    for category in categories:
        templates = library.get_templates_by_category(category)
        print(f"\n{category}:")
        for template in templates:
            print(f"  ✓ {template.name}")
            params = template.get_parameters()
            print(f"    Parameters: {len(params)}")
            for param in params:
                print(f"      - {param['label']}: {param['min']}-{param['max']} (default: {param['default']})")
            total_templates += 1
    
    print("\n" + "=" * 60)
    print(f"Total templates: {total_templates}")
    print("=" * 60)
    
    # Тестируем генерацию путей
    print("\n" + "=" * 60)
    print("Testing Path Generation:")
    print("=" * 60)
    
    all_templates = library.get_all_templates()
    for template in all_templates:
        try:
            params = {p['name']: p['default'] for p in template.get_parameters()}
            path = template.generate_path(**params)
            print(f"✓ {template.name}: Path generated successfully")
        except Exception as e:
            print(f"✗ {template.name}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_pattern_library()
