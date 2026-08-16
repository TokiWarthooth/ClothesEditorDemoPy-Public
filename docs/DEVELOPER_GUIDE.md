# Developer Guide - Clothing Designer

## 🏗️ Архитектура проекта

### Структура файлов

```
ClothesEditorDemoPy-Public/
├── main.py                          # Точка входа приложения
├── requirements.txt                 # Зависимости Python
│
├── app/                             # Основной пакет приложения
│   ├── __init__.py
│   ├── main_window.py              # Главное окно приложения
│   ├── canvas.py                   # Холст для рисования
│   ├── startup_dialog.py           # Стартовое окно
│   ├── tool_manager.py             # Менеджер инструментов
│   ├── pattern_templates.py        # ⭐ Библиотека шаблонов
│   ├── pattern_panel.py            # ⭐ Панель управления шаблонами
│   │
│   └── tools/                      # Инструменты рисования
│       ├── __init__.py
│       ├── base_tool.py            # Базовый класс инструмента
│       ├── pen_tool.py             # Инструмент рисования
│       ├── line_tool.py            # Инструмент линий
│       ├── bezier_tool.py          # Инструмент кривых Безье
│       ├── pattern_tool.py         # ⭐ Инструмент шаблонов
│       └── ...
│
├── test_patterns.py                # Тесты библиотеки шаблонов
├── demo_info.py                    # Демонстрационная информация
│
└── docs/                           # Документация
    ├── README.md
    ├── QUICK_START_RU.md
    ├── PATTERN_TEMPLATES_GUIDE.md
    ├── FEATURES.md
    ├── CHANGELOG.md
    └── SUMMARY.md
```

## 🔧 Как добавить новый шаблон

### Шаг 1: Создать класс шаблона

```python
# В файле app/pattern_templates.py

class MyNewTemplate(PatternTemplate):
    """Описание вашего шаблона"""
    def __init__(self):
        super().__init__("My Template Name", "Category Name")
        
    def generate_path(self, param1=100, param2=200, **kwargs):
        """Генерирует QPainterPath для шаблона"""
        path = QPainterPath()
        
        # Создайте форму используя методы QPainterPath:
        # path.moveTo(x, y)
        # path.lineTo(x, y)
        # path.cubicTo(c1, c2, end)
        # path.quadTo(control, end)
        # path.arcTo(rect, startAngle, sweepLength)
        
        return path
        
    def get_parameters(self):
        """Возвращает список настраиваемых параметров"""
        return [
            {
                "name": "param1",           # Имя параметра (для кода)
                "label": "Parameter 1",     # Отображаемое имя
                "min": 50,                  # Минимальное значение
                "max": 300,                 # Максимальное значение
                "default": 100              # Значение по умолчанию
            },
            {
                "name": "param2",
                "label": "Parameter 2",
                "min": 100,
                "max": 500,
                "default": 200
            }
        ]
```

### Шаг 2: Добавить в библиотеку

```python
# В классе PatternLibrary в app/pattern_templates.py

class PatternLibrary:
    def __init__(self):
        self.templates = {
            "Existing Category": [ExistingTemplate()],
            "New Category": [MyNewTemplate()],  # Новая категория
            # или добавить в существующую:
            "Existing Category": [
                ExistingTemplate(),
                MyNewTemplate()  # Добавить в существующую
            ]
        }
```

### Шаг 3: Тестирование

```bash
# Запустить тесты
python3 test_patterns.py

# Запустить приложение
python3 main.py
```

## 🎨 Примеры создания форм

### Простой прямоугольник

```python
def generate_path(self, width=100, height=200, **kwargs):
    path = QPainterPath()
    path.moveTo(0, 0)
    path.lineTo(width, 0)
    path.lineTo(width, height)
    path.lineTo(0, height)
    path.lineTo(0, 0)
    return path
```

### Прямоугольник с закругленными углами

```python
def generate_path(self, width=100, height=200, radius=10, **kwargs):
    path = QPainterPath()
    path.moveTo(radius, 0)
    path.lineTo(width - radius, 0)
    path.arcTo(width - radius * 2, 0, radius * 2, radius * 2, 90, -90)
    path.lineTo(width, height - radius)
    path.arcTo(width - radius * 2, height - radius * 2, radius * 2, radius * 2, 0, -90)
    path.lineTo(radius, height)
    path.arcTo(0, height - radius * 2, radius * 2, radius * 2, 270, -90)
    path.lineTo(0, radius)
    path.arcTo(0, 0, radius * 2, radius * 2, 180, -90)
    return path
```

### Кривая Безье

```python
def generate_path(self, width=100, height=200, curve=30, **kwargs):
    path = QPainterPath()
    path.moveTo(0, 0)
    
    # Кубическая кривая Безье
    control1 = QPointF(width * 0.3, -curve)
    control2 = QPointF(width * 0.7, -curve)
    end = QPointF(width, 0)
    path.cubicTo(control1, control2, end)
    
    path.lineTo(width, height)
    path.lineTo(0, height)
    path.lineTo(0, 0)
    return path
```

### Квадратичная кривая

```python
def generate_path(self, width=100, height=200, **kwargs):
    path = QPainterPath()
    path.moveTo(0, 0)
    
    # Квадратичная кривая
    control = QPointF(width / 2, -30)
    end = QPointF(width, 0)
    path.quadTo(control, end)
    
    path.lineTo(width, height)
    path.lineTo(0, height)
    path.lineTo(0, 0)
    return path
```

## 🔌 Интеграция нового инструмента

### Шаг 1: Создать класс инструмента

```python
# В файле app/tools/my_tool.py

from PyQt6.QtCore import Qt
from .base_tool import Tool

class MyTool(Tool):
    def __init__(self):
        # Инициализация состояния
        pass
        
    def mouse_press(self, event, canvas):
        """Обработка нажатия мыши"""
        pos = canvas.mapToScene(event.pos())
        # Ваша логика
        
    def mouse_move(self, event, canvas):
        """Обработка движения мыши"""
        pos = canvas.mapToScene(event.pos())
        # Ваша логика
        
    def mouse_release(self, event, canvas):
        """Обработка отпускания мыши"""
        # Ваша логика
        
    def get_cursor(self):
        """Возвращает курсор для инструмента"""
        return Qt.CursorShape.CrossCursor
```

### Шаг 2: Добавить в ToolManager

```python
# В файле app/tool_manager.py

from .tools.my_tool import MyTool

class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.tools = {
            # ... существующие инструменты
            "mytool": MyTool()
        }
```

## 📊 Работа с QPainterPath

### Основные методы

```python
path = QPainterPath()

# Перемещение без рисования
path.moveTo(x, y)
path.moveTo(QPointF(x, y))

# Прямая линия
path.lineTo(x, y)

# Кубическая кривая Безье (2 контрольные точки)
path.cubicTo(c1x, c1y, c2x, c2y, endx, endy)
path.cubicTo(QPointF(c1x, c1y), QPointF(c2x, c2y), QPointF(endx, endy))

# Квадратичная кривая Безье (1 контрольная точка)
path.quadTo(cx, cy, endx, endy)
path.quadTo(QPointF(cx, cy), QPointF(endx, endy))

# Дуга
path.arcTo(x, y, width, height, startAngle, sweepLength)
path.arcTo(QRectF(x, y, width, height), startAngle, sweepLength)

# Закрыть путь (соединить с начальной точкой)
path.closeSubpath()
```

### Углы в arcTo

- Углы измеряются в градусах
- 0° - направление на 3 часа (вправо)
- 90° - направление на 12 часов (вверх)
- 180° - направление на 9 часов (влево)
- 270° - направление на 6 часов (вниз)
- Положительные значения - против часовой стрелки
- Отрицательные значения - по часовой стрелке

## 🧪 Тестирование

### Запуск тестов

```bash
# Тест библиотеки шаблонов
python3 test_patterns.py

# Проверка синтаксиса
python3 -m py_compile app/pattern_templates.py
python3 -m py_compile app/pattern_panel.py
python3 -m py_compile app/tools/pattern_tool.py
```

### Создание нового теста

```python
# В файле test_my_feature.py

def test_my_feature():
    """Тестирует новую функцию"""
    # Arrange
    # Act
    # Assert
    pass

if __name__ == "__main__":
    test_my_feature()
```

## 📝 Стиль кода

### Именование

- **Классы**: PascalCase (например, `PatternTemplate`)
- **Функции/методы**: snake_case (например, `generate_path`)
- **Константы**: UPPER_CASE (например, `DEFAULT_WIDTH`)
- **Приватные**: префикс `_` (например, `_internal_method`)

### Документация

```python
class MyClass:
    """Краткое описание класса.
    
    Более подробное описание, если необходимо.
    """
    
    def my_method(self, param1, param2):
        """Краткое описание метода.
        
        Args:
            param1: Описание первого параметра
            param2: Описание второго параметра
            
        Returns:
            Описание возвращаемого значения
        """
        pass
```

## 🐛 Отладка

### Логирование

```python
# Добавить в начало файла
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Использование
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Отладка в PyQt6

```python
# Вывод информации о событиях
def mouse_press(self, event, canvas):
    pos = canvas.mapToScene(event.pos())
    print(f"Mouse pressed at: {pos.x()}, {pos.y()}")
```

## 🚀 Развертывание

### Создание исполняемого файла (опционально)

```bash
# Установить PyInstaller
pip3 install pyinstaller

# Создать исполняемый файл
pyinstaller --onefile --windowed main.py
```

## 📚 Полезные ресурсы

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt Documentation](https://doc.qt.io/)
- [QPainterPath Reference](https://doc.qt.io/qt-6/qpainterpath.html)
- [Python Style Guide (PEP 8)](https://pep8.org/)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей
