# app/tools/line_tool.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath
from .base_tool import Tool

class LineTool(Tool):
    def __init__(self):
        self.mode = "create"  # Режимы: create, curve, move
        self.points = []  # Точки для новой линии
        self.lines = []  # Список всех созданных линий
        self.selected_line_index = -1  # Индекс выбранной линии
        self.selected_point = None
        self.preview_path = None
        self.edit_points = []  # Точки для редактирования
        self.pen_width = 2
        self.pen_color = QColor("red")
        self.snap_to_grid = True
        self.move_offset = QPointF(0, 0)
        
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
        elif self.mode == "move" and self.selected_point == "all":
            self.move_all_points(pos, canvas)
            
        canvas.viewport().update()
        
    def mouse_release(self, event, canvas):
        if self.selected_point is not None:
            self.selected_point = None
        canvas.viewport().update()
            
    def handle_create_mode(self, pos, canvas):
        if not self.points:
            # Начало новой линии
            self.points.append(pos)
        elif len(self.points) == 1:
            # Завершение линии
            self.points.append(pos)
            self.finish_line(canvas)
            
    def handle_curve_mode(self, pos, canvas):
        # Сбрасываем выделение если кликнули мимо линий
        if not self.select_line_near_point(pos):
            self.selected_line_index = -1
            self.edit_points = []
        else:
            # Выбираем точку для редактирования
            self.select_edit_point(pos)
            
    def handle_move_mode(self, pos, canvas):
        if self.select_line_near_point(pos):
            self.selected_point = "all"
            selected_line = self.lines[self.selected_line_index]
            self.move_offset = pos - selected_line['points'][0]
            
    def finish_line(self, canvas):
        """Завершает создание линии и добавляет её в список"""
        if len(self.points) == 2:
            path = QPainterPath()
            path.moveTo(self.points[0])
            path.lineTo(self.points[1])
            
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            
            path_item = canvas.scene.addPath(path, pen)
            
            # Сохраняем линию в список
            line_data = {
                'points': self.points.copy(),
                'path_item': path_item,
                'is_curve': False,
                'control_point': None
            }
            self.lines.append(line_data)
            
            # Сбрасываем состояние для новой линии
            self.points = []
            if self.preview_path:
                canvas.scene.removeItem(self.preview_path)
                self.preview_path = None
            
    def select_line_near_point(self, pos):
        """Выбирает линию near точки и возвращает True если найдена"""
        for i, line_data in enumerate(self.lines):
            if self.is_point_near_line(pos, line_data['points'], 15):
                self.selected_line_index = i
                self.generate_edit_points(line_data)
                return True
        return False
        
    def generate_edit_points(self, line_data):
        """Создает точки редактирования для выбранной линии"""
        points = line_data['points']
        if len(points) == 2:
            self.edit_points = [
                points[0],  # Начальная точка
                points[1],  # Конечная точка
                QPointF((points[0].x() + points[1].x()) / 2,  # Середина
                       (points[0].y() + points[1].y()) / 2)
            ]
            
    def select_edit_point(self, pos):
        """Выбирает точку редактирования"""
        for i, point in enumerate(self.edit_points):
            if self.distance(pos, point) < 8:
                self.selected_point = i
                return
                
    def move_edit_point(self, pos, canvas):
        """Перемещает выбранную точку редактирования"""
        if self.selected_line_index == -1:
            return
            
        line_data = self.lines[self.selected_line_index]
        
        if self.selected_point == 0:  # Начальная точка
            line_data['points'][0] = pos
        elif self.selected_point == 1:  # Конечная точка
            line_data['points'][1] = pos
        elif self.selected_point == 2:  # Середина - создаем кривую
            # Превращаем в кривую Безье
            start = line_data['points'][0]
            end = line_data['points'][1]
            
            path = QPainterPath()
            path.moveTo(start)
            path.quadTo(pos, end)
            
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            
            # Обновляем графический элемент
            canvas.scene.removeItem(line_data['path_item'])
            line_data['path_item'] = canvas.scene.addPath(path, pen)
            line_data['is_curve'] = True
            line_data['control_point'] = pos
            
            self.edit_points[2] = pos  # Обновляем позицию контрольной точки
            return
            
        # Обновляем прямую линию
        self.update_line(line_data, canvas)
            
    def update_line(self, line_data, canvas):
        """Обновляет графическое представление линии"""
        path = QPainterPath()
        path.moveTo(line_data['points'][0])
        path.lineTo(line_data['points'][1])
        
        line_data['path_item'].setPath(path)
        line_data['is_curve'] = False
        line_data['control_point'] = None
        
    def move_all_points(self, pos, canvas):
        """Перемещает всю линию"""
        if self.selected_line_index == -1:
            return
            
        line_data = self.lines[self.selected_line_index]
        offset = pos - line_data['points'][0] - self.move_offset
        
        for i in range(len(line_data['points'])):
            line_data['points'][i] += offset
            
        if line_data['control_point']:
            line_data['control_point'] += offset
            
        # Перерисовываем линию
        if line_data['is_curve']:
            path = QPainterPath()
            path.moveTo(line_data['points'][0])
            path.quadTo(line_data['control_point'], line_data['points'][1])
            line_data['path_item'].setPath(path)
        else:
            self.update_line(line_data, canvas)
            
        # Обновляем точки редактирования
        self.generate_edit_points(line_data)
            
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
        if self.mode == "create" and self.points:
            self.points = []
            if self.preview_path:
                canvas.scene.removeItem(self.preview_path)
                self.preview_path = None
        else:
            self.selected_point = None
            self.selected_line_index = -1
            self.edit_points = []
            
    def reset(self, canvas=None):
        """Полностью сбрасывает инструмент"""
        self.points = []
        self.selected_point = None
        self.selected_line_index = -1
        self.edit_points = []
        
        if canvas:
            # Удаляем preview
            if self.preview_path:
                try:
                    canvas.scene.removeItem(self.preview_path)
                except:
                    pass
                self.preview_path = None
            
            # Удаляем все линии
            for line_data in self.lines:
                try:
                    canvas.scene.removeItem(line_data['path_item'])
                except:
                    pass
            
            self.lines = []
            
    def draw_edit_points(self, painter, canvas):
        """Рисует точки для редактирования выбранной линии"""
        if self.mode == "curve" and self.selected_line_index != -1 and self.edit_points:
            for point in self.edit_points:
                painter.setPen(QPen(QColor("blue"), 2))
                painter.setBrush(QColor("lightblue"))
                painter.drawEllipse(point, 4, 4)
                
    def distance(self, point1, point2):
        return ((point1.x() - point2.x()) ** 2 + (point1.y() - point2.y()) ** 2) ** 0.5
        
    def is_point_near_line(self, point, line_points, tolerance=10):
        """Проверяет, находится ли точка близко к линии"""
        if len(line_points) != 2:
            return False
        return self.is_point_on_segment(point, line_points[0], line_points[1], tolerance)
        
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
        # Обновляем все линии
        for line_data in self.lines:
            pen = line_data['path_item'].pen()
            pen.setWidth(width)
            line_data['path_item'].setPen(pen)
            
    def set_pen_color(self, color):
        self.pen_color = color
        # Обновляем все линии
        for line_data in self.lines:
            pen = line_data['path_item'].pen()
            pen.setColor(color)
            line_data['path_item'].setPen(pen)
            
    def set_mode(self, mode):
        self.mode = mode
        self.selected_point = None
        self.selected_line_index = -1
        if mode != "curve":
            self.edit_points = []
        
    def toggle_snap_to_grid(self, enabled):
        self.snap_to_grid = enabled
        
    def get_cursor(self):
        if self.mode == "curve":
            return Qt.CursorShape.PointingHandCursor
        return Qt.CursorShape.CrossCursor