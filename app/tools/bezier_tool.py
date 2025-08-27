# app/tools/bezier_tool.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainterPath, QPen, QColor, QBrush
from .base_tool import Tool

class BezierTool(Tool):
    def __init__(self):
        self.mode = "create"  # Режимы: create, edit, move
        self.points = []  # Точки кривой Безье
        self.control_points = []  # Контрольные точки
        self.selected_point = None
        self.current_path = None
        self.preview_path = None
        self.pen_width = 2
        self.pen_color = QColor("blue")
        
    def mouse_press(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "create":
                self.handle_create_mode(pos, canvas)
            elif self.mode == "edit":
                self.handle_edit_mode(pos, canvas)
            elif self.mode == "move":
                self.handle_move_mode(pos, canvas)
                
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancel_operation(canvas)
            
    def mouse_move(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if self.mode == "create" and self.points:
            self.update_preview(pos, canvas)
        elif self.mode == "edit" and self.selected_point:
            self.move_point(pos, canvas)
        elif self.mode == "move" and self.selected_point:
            self.move_curve(pos, canvas)
            
        canvas.viewport().update()
        
    def mouse_release(self, event, canvas):
        if self.selected_point:
            self.selected_point = None
            canvas.viewport().update()
            
    def handle_create_mode(self, pos, canvas):
        if not self.points:
            # Первая точка кривой
            self.points.append(pos)
            self.control_points.append(None)  # Пока нет контрольной точки
        elif len(self.points) == 1:
            # Вторая точка + контрольная точка
            self.points.append(pos)
            control_pos = QPointF(pos.x() + 50, pos.y() - 50)  # Автоматическая контрольная точка
            self.control_points.append(control_pos)
            self.create_bezier_curve(canvas)
        else:
            # Добавление новой сегмента кривой
            last_point = self.points[-1]
            self.points.append(pos)
            # Создаем симметричную контрольную точку для плавности
            prev_control = self.control_points[-1]
            if prev_control:
                dx = last_point.x() - prev_control.x()
                dy = last_point.y() - prev_control.y()
                new_control = QPointF(pos.x() - dx, pos.y() - dy)
                self.control_points.append(new_control)
            else:
                self.control_points.append(QPointF(pos.x() - 50, pos.y() - 50))
            
            self.update_bezier_curve(canvas)
            
    def handle_edit_mode(self, pos, canvas):
        # Поиск ближайшей точки для редактирования
        for i, point in enumerate(self.points):
            if self.distance(pos, point) < 10:  # Радиус захвата точки
                self.selected_point = ("point", i)
                return
                
        for i, cpoint in enumerate(self.control_points):
            if cpoint and self.distance(pos, cpoint) < 8:  # Меньший радиус для контрольных точек
                self.selected_point = ("control", i)
                return
                
    def handle_move_mode(self, pos, canvas):
        # Поиск кривой для перемещения
        if self.current_path and self.current_path.contains(pos):
            self.selected_point = ("curve", 0)
            self.move_offset = pos - self.points[0] if self.points else QPointF(0, 0)
            
    def create_bezier_curve(self, canvas):
        if len(self.points) >= 2:
            path = QPainterPath()
            path.moveTo(self.points[0])
            
            for i in range(1, len(self.points)):
                if self.control_points[i]:
                    # Кривая Безье с контрольной точкой
                    path.cubicTo(self.control_points[i], 
                                self.control_points[i], 
                                self.points[i])
                else:
                    # Прямая линия
                    path.lineTo(self.points[i])
            
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
            self.current_path = canvas.scene.addPath(path, pen)
            
    def update_bezier_curve(self, canvas):
        if self.current_path and len(self.points) >= 2:
            path = QPainterPath()
            path.moveTo(self.points[0])
            
            for i in range(1, len(self.points)):
                if self.control_points[i]:
                    path.cubicTo(self.control_points[i], 
                                self.control_points[i], 
                                self.points[i])
                else:
                    path.lineTo(self.points[i])
            
            self.current_path.setPath(path)
            
    def update_preview(self, pos, canvas):
        if len(self.points) >= 1:
            path = QPainterPath()
            path.moveTo(self.points[0])
            
            # Предпросмотр текущего сегмента
            if len(self.points) == 1:
                path.lineTo(pos)
            else:
                last_control = self.control_points[-1]
                if last_control:
                    path.cubicTo(last_control, last_control, pos)
                else:
                    path.lineTo(pos)
            
            pen = QPen(QColor(100, 100, 100, 150), 1, Qt.PenStyle.DashLine)
            if self.preview_path:
                canvas.scene.removeItem(self.preview_path)
            self.preview_path = canvas.scene.addPath(path, pen)
            
    def move_point(self, pos, canvas):
        if self.selected_point[0] == "point":
            index = self.selected_point[1]
            self.points[index] = pos
            self.update_bezier_curve(canvas)
        elif self.selected_point[0] == "control":
            index = self.selected_point[1]
            self.control_points[index] = pos
            self.update_bezier_curve(canvas)
            
    def move_curve(self, pos, canvas):
        if self.selected_point[0] == "curve" and self.points:
            offset = pos - self.points[0] - self.move_offset
            for i in range(len(self.points)):
                self.points[i] += offset
            for i in range(len(self.control_points)):
                if self.control_points[i]:
                    self.control_points[i] += offset
            self.update_bezier_curve(canvas)
            
    def cancel_operation(self, canvas):
        if self.mode == "create":
            if self.points:
                self.points.pop()
                if self.control_points:
                    self.control_points.pop()
                if not self.points:
                    self.reset(canvas)
                else:
                    self.update_bezier_curve(canvas)
        else:
            self.reset(canvas)
            
    def reset(self, canvas):
        self.points = []
        self.control_points = []
        self.selected_point = None
        if self.preview_path:
            canvas.scene.removeItem(self.preview_path)
            self.preview_path = None
        if self.current_path:
            canvas.scene.removeItem(self.current_path)
            self.current_path = None
            
    def distance(self, point1, point2):
        return ((point1.x() - point2.x()) ** 2 + (point1.y() - point2.y()) ** 2) ** 0.5
        
    def set_pen_width(self, width):
        self.pen_width = width
        if self.current_path:
            pen = self.current_path.pen()
            pen.setWidth(width)
            self.current_path.setPen(pen)
            
    def set_pen_color(self, color):
        self.pen_color = color
        if self.current_path:
            pen = self.current_path.pen()
            pen.setColor(color)
            self.current_path.setPen(pen)
            
    def set_mode(self, mode):
        self.mode = mode
        self.reset(None)
        
    def get_cursor(self):
        return Qt.CursorShape.CrossCursor
        
    def get_settings(self):
        """Возвращает настройки инструмента для панели свойств"""
        return {
            "width": self.pen_width,
            "color": self.pen_color,
            "mode": self.mode
        }