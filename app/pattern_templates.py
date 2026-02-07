# app/pattern_templates.py
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath
import math

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
        
    def generate_path(self, width=150, height=400, curve_depth=30, **kwargs):
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
            {"name": "width", "label": "Width", "min": 100, "max": 300, "default": 150},
            {"name": "height", "label": "Height", "min": 200, "max": 600, "default": 400},
            {"name": "curve_depth", "label": "Curve Depth", "min": 10, "max": 60, "default": 30}
        ]


class CollarTemplate(PatternTemplate):
    """Шаблон воротника"""
    def __init__(self):
        super().__init__("Collar", "Collars")
        
    def generate_path(self, width=200, height=80, neck_curve=40, **kwargs):
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
            {"name": "width", "label": "Width", "min": 100, "max": 400, "default": 200},
            {"name": "height", "label": "Height", "min": 40, "max": 150, "default": 80},
            {"name": "neck_curve", "label": "Neck Curve", "min": 20, "max": 80, "default": 40}
        ]


class PocketTemplate(PatternTemplate):
    """Шаблон кармана"""
    def __init__(self):
        super().__init__("Pocket", "Pockets")
        
    def generate_path(self, width=120, height=140, corner_radius=15, **kwargs):
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
            {"name": "width", "label": "Width", "min": 60, "max": 200, "default": 120},
            {"name": "height", "label": "Height", "min": 80, "max": 250, "default": 140},
            {"name": "corner_radius", "label": "Corner Radius", "min": 5, "max": 40, "default": 15}
        ]


class SkirtTemplate(PatternTemplate):
    """Шаблон юбки (передняя/задняя панель)"""
    def __init__(self):
        super().__init__("Skirt Panel", "Skirts")
        
    def generate_path(self, waist_width=180, hip_width=220, length=500, **kwargs):
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
            {"name": "waist_width", "label": "Waist Width", "min": 100, "max": 300, "default": 180},
            {"name": "hip_width", "label": "Hip Width", "min": 150, "max": 400, "default": 220},
            {"name": "length", "label": "Length", "min": 200, "max": 800, "default": 500}
        ]


class TrouserLegTemplate(PatternTemplate):
    """Шаблон штанины"""
    def __init__(self):
        super().__init__("Trouser Leg", "Trousers")
        
    def generate_path(self, waist_width=200, hip_width=240, leg_width=180, length=900, **kwargs):
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
            {"name": "waist_width", "label": "Waist Width", "min": 120, "max": 350, "default": 200},
            {"name": "hip_width", "label": "Hip Width", "min": 150, "max": 400, "default": 240},
            {"name": "leg_width", "label": "Leg Width", "min": 100, "max": 300, "default": 180},
            {"name": "length", "label": "Length", "min": 500, "max": 1200, "default": 900}
        ]


class BodyTemplate(PatternTemplate):
    """Шаблон лифа (передняя часть)"""
    def __init__(self):
        super().__init__("Bodice Front", "Bodice")
        
    def generate_path(self, width=200, length=400, shoulder_width=140, neck_depth=80, **kwargs):
        path = QPainterPath()
        
        # Начинаем с левого плеча
        path.moveTo(0, 0)
        
        # Плечо
        path.lineTo(shoulder_width, 0)
        
        # Пройма (изогнутая линия)
        armhole_depth = length * 0.3
        control1 = QPointF(shoulder_width + 20, armhole_depth * 0.3)
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
            {"name": "width", "label": "Width", "min": 150, "max": 350, "default": 200},
            {"name": "length", "label": "Length", "min": 250, "max": 600, "default": 400},
            {"name": "shoulder_width", "label": "Shoulder Width", "min": 80, "max": 200, "default": 140},
            {"name": "neck_depth", "label": "Neck Depth", "min": 40, "max": 150, "default": 80}
        ]


class PatternLibrary:
    """Библиотека всех доступных шаблонов"""
    def __init__(self):
        self.templates = {
            "Sleeves": [SleeveTemplate()],
            "Collars": [CollarTemplate()],
            "Pockets": [PocketTemplate()],
            "Skirts": [SkirtTemplate()],
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
