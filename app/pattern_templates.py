# app/pattern_templates.py
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath
import math
from .measurements import MeasurementSystem

# Все параметры шаблонов (width/height/length и т.д.) задаются в РЕАЛЬНЫХ
# сантиметрах — так же, как линейка, припуски на швы и панель Pattern Size.
# generate_path() переводит их в px сцены через этот коэффициент.
PX_PER_CM = MeasurementSystem.PX_PER_CM


class PatternTemplate:
    """Базовый класс для шаблонов выкроек"""
    def __init__(self, name, category):
        self.name = name
        self.category = category
        
    def generate_path(self, width, height, **kwargs):
        """Генерирует QPainterPath для шаблона"""
        raise NotImplementedError
        
    def get_parameters(self):
        """Возвращает список настраиваемых параметров"""
        return []


class SleeveTemplate(PatternTemplate):
    """Шаблон рукава"""
    def __init__(self):
        super().__init__("Sleeve", "Sleeves")
        
    def generate_path(self, width=34, height=58, curve_depth=5, **kwargs):
        width *= PX_PER_CM
        height *= PX_PER_CM
        curve_depth *= PX_PER_CM
        path = QPainterPath()

        # Начинаем с верхней точки (окат рукава)
        path.moveTo(0, curve_depth)
        
        # Окат рукава (плавная кривая)
        control1 = QPointF(width * 0.3, -curve_depth)
        control2 = QPointF(width * 0.7, -curve_depth)
        end = QPointF(width, curve_depth)
        path.cubicTo(control1, control2, end)
        
        # Правая сторона рукава (слегка сужается к низу)
        path.lineTo(width * 0.85, height)
        
        # Низ рукава
        path.lineTo(width * 0.15, height)
        
        # Левая сторона рукава
        path.lineTo(0, curve_depth)
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "width", "label": "Width (cm)", "min": 25, "max": 45, "default": 34},
            {"name": "height", "label": "Height (cm)", "min": 45, "max": 70, "default": 58},
            {"name": "curve_depth", "label": "Curve Depth (cm)", "min": 3, "max": 8, "default": 5}
        ]


class CollarTemplate(PatternTemplate):
    """Шаблон воротника"""
    def __init__(self):
        super().__init__("Collar", "Collars")
        
    def generate_path(self, width=40, height=7, neck_curve=4, **kwargs):
        width *= PX_PER_CM
        height *= PX_PER_CM
        neck_curve *= PX_PER_CM
        path = QPainterPath()

        # Начинаем с левого нижнего угла
        path.moveTo(0, height)
        
        # Левая сторона
        path.lineTo(0, height * 0.3)
        
        # Вырез горловины (кривая)
        control1 = QPointF(width * 0.2, -neck_curve)
        control2 = QPointF(width * 0.8, -neck_curve)
        end = QPointF(width, height * 0.3)
        path.cubicTo(control1, control2, end)
        
        # Правая сторона
        path.lineTo(width, height)
        
        # Нижняя часть (слегка изогнутая)
        control = QPointF(width * 0.5, height * 1.1)
        path.quadTo(control, QPointF(0, height))
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "width", "label": "Width (cm)", "min": 30, "max": 50, "default": 40},
            {"name": "height", "label": "Height (cm)", "min": 4, "max": 12, "default": 7},
            {"name": "neck_curve", "label": "Neck Curve (cm)", "min": 2, "max": 8, "default": 4}
        ]


class PocketTemplate(PatternTemplate):
    """Шаблон кармана"""
    def __init__(self):
        super().__init__("Pocket", "Pockets")
        
    def generate_path(self, width=14, height=16, corner_radius=2, **kwargs):
        width *= PX_PER_CM
        height *= PX_PER_CM
        corner_radius *= PX_PER_CM
        path = QPainterPath()

        # Прямоугольный карман с закругленными углами
        path.moveTo(corner_radius, 0)
        path.lineTo(width - corner_radius, 0)
        
        # Верхний правый угол
        path.arcTo(width - corner_radius * 2, 0, corner_radius * 2, corner_radius * 2, 90, -90)
        
        # Правая сторона
        path.lineTo(width, height - corner_radius)
        
        # Нижний правый угол
        path.arcTo(width - corner_radius * 2, height - corner_radius * 2, 
                   corner_radius * 2, corner_radius * 2, 0, -90)
        
        # Низ
        path.lineTo(corner_radius, height)
        
        # Нижний левый угол
        path.arcTo(0, height - corner_radius * 2, corner_radius * 2, corner_radius * 2, 270, -90)
        
        # Левая сторона
        path.lineTo(0, corner_radius)
        
        # Верхний левый угол
        path.arcTo(0, 0, corner_radius * 2, corner_radius * 2, 180, -90)
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "width", "label": "Width (cm)", "min": 10, "max": 20, "default": 14},
            {"name": "height", "label": "Height (cm)", "min": 12, "max": 24, "default": 16},
            {"name": "corner_radius", "label": "Corner Radius (cm)", "min": 1, "max": 5, "default": 2}
        ]


class SkirtTemplate(PatternTemplate):
    """Шаблон юбки (передняя/задняя панель)"""
    def __init__(self):
        super().__init__("Skirt Panel", "Skirts")
        
    def generate_path(self, waist_width=36, hip_width=46, length=58, **kwargs):
        waist_width *= PX_PER_CM
        hip_width *= PX_PER_CM
        length *= PX_PER_CM
        path = QPainterPath()

        # Начинаем с левого верхнего угла (талия)
        path.moveTo(0, 0)
        
        # Верх (талия)
        path.lineTo(waist_width, 0)
        
        # Правая сторона (расширение к бедрам)
        hip_point = length * 0.3  # Бедра на 30% длины
        path.lineTo(waist_width + (hip_width - waist_width) / 2, hip_point)
        
        # Продолжение до низа
        path.lineTo(waist_width + (hip_width - waist_width) / 2, length)
        
        # Низ юбки
        path.lineTo((hip_width - waist_width) / 2, length)
        
        # Левая сторона
        path.lineTo(0, hip_point)
        path.lineTo(0, 0)
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "waist_width", "label": "Waist Width (cm)", "min": 28, "max": 45, "default": 36},
            {"name": "hip_width", "label": "Hip Width (cm)", "min": 38, "max": 55, "default": 46},
            {"name": "length", "label": "Length (cm)", "min": 40, "max": 90, "default": 58}
        ]


class SkirtTemplate2(PatternTemplate):
    """Юбка-полоска: постоянная ширина (без расширения к бёдрам), с двумя
    вытачками (треугольными вырезами) на линии талии, выше линии бёдер."""

    def __init__(self):
        super().__init__("Skirt Strip (Darts)", "Skirts")

    def generate_path(self, width=51, length=72, dart_width=3, dart_depth=10, **kwargs):
        width *= PX_PER_CM
        length *= PX_PER_CM
        dart_width *= PX_PER_CM
        dart_depth *= PX_PER_CM
        path = QPainterPath()

        # Вытачки симметрично на 30% и 70% ширины
        dart1 = width * 0.3
        dart2 = width * 0.7

        # Верхний край (линия талии) с двумя треугольными вытачками —
        # "пустое пространство", вырезанное для посадки по талии
        path.moveTo(0, 0)
        path.lineTo(dart1 - dart_width / 2, 0)
        path.lineTo(dart1, dart_depth)
        path.lineTo(dart1 + dart_width / 2, 0)
        path.lineTo(dart2 - dart_width / 2, 0)
        path.lineTo(dart2, dart_depth)
        path.lineTo(dart2 + dart_width / 2, 0)
        path.lineTo(width, 0)

        # Правая сторона
        path.lineTo(width, length)

        # Низ
        path.lineTo(0, length)

        # Левая сторона
        path.lineTo(0, 0)

        return path

    def get_parameters(self):
        return [
            {"name": "width", "label": "Width (cm)", "min": 30, "max": 70, "default": 51},
            {"name": "length", "label": "Length (cm)", "min": 50, "max": 100, "default": 72},
            {"name": "dart_width", "label": "Dart Width (cm)", "min": 1, "max": 6, "default": 3},
            {"name": "dart_depth", "label": "Dart Depth (cm)", "min": 5, "max": 18, "default": 10}
        ]


class TrouserLegTemplate(PatternTemplate):
    """Шаблон штанины"""
    def __init__(self):
        super().__init__("Trouser Leg", "Trousers")
        
    def generate_path(self, waist_width=42, hip_width=50, leg_width=22, length=100, **kwargs):
        waist_width *= PX_PER_CM
        hip_width *= PX_PER_CM
        leg_width *= PX_PER_CM
        length *= PX_PER_CM
        path = QPainterPath()

        # Начинаем с левого верхнего угла
        path.moveTo(0, 0)
        
        # Верх (талия)
        path.lineTo(waist_width, 0)
        
        # Правая сторона
        hip_point = length * 0.2
        knee_point = length * 0.6
        
        # До бедра
        path.lineTo(waist_width + (hip_width - waist_width) / 2, hip_point)
        
        # До колена (сужение)
        path.lineTo(waist_width - (waist_width - leg_width) / 2, knee_point)
        
        # До низа
        path.lineTo(waist_width - (waist_width - leg_width) / 2, length)
        
        # Низ
        path.lineTo((waist_width - leg_width) / 2, length)
        
        # Левая сторона (зеркально)
        path.lineTo((waist_width - leg_width) / 2, knee_point)
        path.lineTo((hip_width - waist_width) / 2, hip_point)
        path.lineTo(0, 0)
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "waist_width", "label": "Waist Width (cm)", "min": 35, "max": 55, "default": 42},
            {"name": "hip_width", "label": "Hip Width (cm)", "min": 40, "max": 60, "default": 50},
            {"name": "leg_width", "label": "Leg Width (cm)", "min": 16, "max": 30, "default": 22},
            {"name": "length", "label": "Length (cm)", "min": 85, "max": 115, "default": 100}
        ]


class BodyTemplate(PatternTemplate):
    """Шаблон лифа (передняя часть)"""
    def __init__(self):
        super().__init__("Bodice Front", "Bodice")
        
    def generate_path(self, width=45, length=42, shoulder_width=18, neck_depth=8, **kwargs):
        width *= PX_PER_CM
        length *= PX_PER_CM
        shoulder_width *= PX_PER_CM
        neck_depth *= PX_PER_CM
        path = QPainterPath()

        # Начинаем с левого плеча
        path.moveTo(0, 0)
        
        # Плечо
        path.lineTo(shoulder_width, 0)
        
        # Пройма (изогнутая линия)
        armhole_depth = length * 0.3
        # +~14% от ширины плеча — сохраняет ту же пропорцию кривой проймы,
        # что была при старом жёстко заданном смещении "+20" (в старых "сырых"
        # единицах, когда shoulder_width по умолчанию был 140)
        control1 = QPointF(shoulder_width * 1.14, armhole_depth * 0.3)
        control2 = QPointF(width, armhole_depth * 0.7)
        path.cubicTo(control1, control2, QPointF(width, armhole_depth))
        
        # Боковой шов
        path.lineTo(width, length)
        
        # Низ
        path.lineTo(width * 0.2, length)
        
        # Левый боковой шов
        path.lineTo(width * 0.2, armhole_depth)
        
        # Левая пройма
        control1 = QPointF(width * 0.2, armhole_depth * 0.7)
        control2 = QPointF(0, armhole_depth * 0.3)
        path.cubicTo(control1, control2, QPointF(0, 0))
        
        return path
        
    def get_parameters(self):
        return [
            {"name": "width", "label": "Width (cm)", "min": 35, "max": 55, "default": 45},
            {"name": "length", "label": "Length (cm)", "min": 35, "max": 50, "default": 42},
            {"name": "shoulder_width", "label": "Shoulder Width (cm)", "min": 14, "max": 24, "default": 18},
            {"name": "neck_depth", "label": "Neck Depth (cm)", "min": 5, "max": 12, "default": 8}
        ]


class PatternLibrary:
    """Библиотека всех доступных шаблонов"""
    def __init__(self):
        self.templates = {
            "Sleeves": [SleeveTemplate()],
            "Collars": [CollarTemplate()],
            "Pockets": [PocketTemplate()],
            "Skirts": [SkirtTemplate(), SkirtTemplate2()],
            "Trousers": [TrouserLegTemplate()],
            "Bodice": [BodyTemplate()]
        }
        
    def get_categories(self):
        """Возвращает список категорий"""
        return list(self.templates.keys())
        
    def get_templates_by_category(self, category):
        """Возвращает шаблоны по категории"""
        return self.templates.get(category, [])
        
    def get_all_templates(self):
        """Возвращает все шаблоны"""
        all_templates = []
        for templates in self.templates.values():
            all_templates.extend(templates)
        return all_templates
