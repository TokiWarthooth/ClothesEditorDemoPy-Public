# app/tools/line_tool.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath
from .base_tool import Tool

class LineTool(Tool):
    def __init__(self):
        self.mode = "create"  # Режимы: create, curve, move
        self.points = []  # Точки линии
        self.control_points = []  # Контрольные точки для кривых
        self.selected_point = None
        self.current_path = None
        self.preview_path = None
        self.edit_points = []  # Точки для редактирования на существующей линии
        self.pen_width = 2
        self.pen_color = QColor("red")
        self.snap_to_grid = True
        
    def mouse_press(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if self.snap_to_grid:
            pos = self.snap_to_grid_position(pos, canvas.grid_size)
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "create":
                self.handle_create_mode(pos, canvas)
            elif self.mode == "curve":
                self.handle_curve_mode(pos, canvas)
            elif self.mode == "move":
                self.handle_move_mode(pos, canvas)
                
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancel_operation(canvas)
            
    def mouse_move(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if self.snap_to_grid:
            pos = self.snap_to_grid_position(pos, canvas.grid_size)
        
        if self.mode == "create" and self.points:
            self.update_preview(pos, canvas)
        elif self.mode == "curve" and self.selected_point is not None:
            self.move_edit_point(pos, canvas)
            
        canvas.viewport().update()
        
    def mouse_release(self, event, canvas):
        if self.selected_point is not None:
            self.selected_point = None
        canvas.viewport().update()
            
    def handle_create_mode(self, pos, canvas):
        if not self.points:
            # Первая точка линии
            self.points.append(pos)
        elif len(self.points) == 1:
            # Вторая точка - завершаем линию
            self.points.append(pos)
            self.create_line(canvas)
            
    def handle_curve_mode(self, pos, canvas):
        if not self.current_path:
            # Если нет линии - ищем ближайшую существующую линию
            self.find_and_select_line(pos, canvas)
        else:
            # Если линия уже выбрана - ищем точку редактирования
            self.select_edit_point(pos)
            
    def handle_move_mode(self, pos, canvas):
        if self.is_point_near_line(pos, 15):
            self.selected_point = "all"
            self.move_offset = pos - self.points[0] if self.points else QPointF(0, 0)
            
    def create_line(self, canvas):
        if len(self.points) == 2:
            path = QPainterPath()
            path.moveTo(self.points[0])
            path.lineTo(self.points[1])
            
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            
            self.current_path = canvas.scene.addPath(path, pen)
            self.generate_edit_points()
            
    def update_line(self, canvas):
        if self.current_path and len(self.points) == 2:
            path = QPainterPath()
            path.moveTo(self.points[0])
            path.lineTo(self.points[1])
            
            self.current_path.setPath(path)
            self.generate_edit_points()
            
    def generate_edit_points(self):
        """Создает точки для редактирования на линии"""
        if len(self.points) == 2:
            self.edit_points = [
                self.points[0],  # Начальная точка
                self.points[1],  # Конечная точка
                QPointF((self.points[0].x() + self.points[1].x()) / 2,  # Середина
                       (self.points[0].y() + self.points[1].y()) / 2)
            ]
            
    def find_and_select_line(self, pos, canvas):
        """Ищет ближайшую линию для редактирования"""
        # Здесь должна быть логика поиска существующих линий на сцене
        # Для простоты будем работать только с текущей линией
        if self.current_path and self.is_point_near_line(pos, 15):
            self.generate_edit_points()
            
    def select_edit_point(self, pos):
        """Выбирает точку редактирования"""
        for i, point in enumerate(self.edit_points):
            if self.distance(pos, point) < 8:
                self.selected_point = i
                return
                
    def move_edit_point(self, pos, canvas):
        """Перемещает выбранную точку редактирования"""
        if self.selected_point == 0:  # Начальная точка
            self.points[0] = pos
        elif self.selected_point == 1:  # Конечная точка
            self.points[1] = pos
        elif self.selected_point == 2:  # Середина - создаем кривую
            # Превращаем прямую линию в кривую
            if len(self.points) == 2:
                # Сохраняем исходные точки
                start = self.points[0]
                end = self.points[1]
                
                # Создаем кривую Безье с контрольной точкой в позиции мыши
                path = QPainterPath()
                path.moveTo(start)
                path.quadTo(pos, end)  # Квадратичная кривая Безье
                
                pen = QPen(self.pen_color, self.pen_width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                
                # Удаляем старую линию и создаем новую кривую
                if self.current_path:
                    canvas.scene.removeItem(self.current_path)
                self.current_path = canvas.scene.addPath(path, pen)
                
                # Обновляем точки для отображения кривой
                self.edit_points = [start, end, pos]
                return
                
        self.update_line(canvas)
            
    def update_preview(self, pos, canvas):
        if len(self.points) == 1:
            path = QPainterPath()
            path.moveTo(self.points[0])
            path.lineTo(pos)
            
            pen = QPen(QColor(100, 100, 100, 150), 1, Qt.PenStyle.DashLine)
            if self.preview_path:
                canvas.scene.removeItem(self.preview_path)
            self.preview_path = canvas.scene.addPath(path, pen)
            
    def cancel_operation(self, canvas):
        if self.mode == "create":
            self.reset(canvas)
        else:
            self.selected_point = None
            
    def reset(self, canvas=None):
        """Сбрасывает состояние инструмента"""
        self.points = []
        self.control_points = []
        self.selected_point = None
        self.edit_points = []
        
        if canvas:
            if self.preview_path:
                try:
                    canvas.scene.removeItem(self.preview_path)
                except:
                    pass
                self.preview_path = None
            
            if self.current_path:
                try:
                    canvas.scene.removeItem(self.current_path)
                except:
                    pass
                self.current_path = None
            
    def draw_edit_points(self, painter, canvas):
        """Рисует точки для редактирования"""
        if self.mode == "curve" and self.edit_points:
            for point in self.edit_points:
                painter.setPen(QPen(QColor("blue"), 2))
                painter.setBrush(QColor("lightblue"))
                painter.drawEllipse(point, 4, 4)
                
    def distance(self, point1, point2):
        return ((point1.x() - point2.x()) ** 2 + (point1.y() - point2.y()) ** 2) ** 0.5
        
    def is_point_near_line(self, point, tolerance=10):
        """Проверяет, находится ли точка близко к линии"""
        if len(self.points) != 2:
            return False
        return self.is_point_on_segment(point, self.points[0], self.points[1], tolerance)
        
    def is_point_on_segment(self, point, start, end, tolerance=5):
        """Проверяет, находится ли точка близко к сегменту линии"""
        segment_vector = QPointF(end.x() - start.x(), end.y() - start.y())
        point_vector = QPointF(point.x() - start.x(), point.y() - start.y())
        
        segment_length = self.distance(start, end)
        if segment_length == 0:
            return False
            
        normalized_segment = QPointF(segment_vector.x() / segment_length, 
                                   segment_vector.y() / segment_length)
        
        projection_length = point_vector.x() * normalized_segment.x() + point_vector.y() * normalized_segment.y()
        
        if projection_length < 0 or projection_length > segment_length:
            return False
            
        projection_point = QPointF(
            start.x() + normalized_segment.x() * projection_length,
            start.y() + normalized_segment.y() * projection_length
        )
        
        return self.distance(point, projection_point) <= tolerance
        
    def snap_to_grid_position(self, position, grid_size):
        if grid_size <= 0:
            return position
        x = round(position.x() / grid_size) * grid_size
        y = round(position.y() / grid_size) * grid_size
        return QPointF(x, y)
        
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
        self.selected_point = None
        if mode != "curve":
            self.edit_points = []
        
    def toggle_snap_to_grid(self, enabled):
        self.snap_to_grid = enabled
        
    def get_cursor(self):
        if self.mode == "curve":
            return Qt.CursorShape.PointingHandCursor
        return Qt.CursorShape.CrossCursor