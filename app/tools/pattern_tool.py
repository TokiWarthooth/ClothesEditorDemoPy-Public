# app/tools/pattern_tool.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush
from .base_tool import Tool

class PatternTool(Tool):
    """Инструмент для размещения и редактирования шаблонов выкроек"""
    def __init__(self):
        self.current_pattern = None
        self.current_params = {}
        self.placed_patterns = []  # Список размещенных шаблонов
        self.selected_pattern = None
        self.dragging = False
        self.drag_offset = QPointF(0, 0)
        self.placement_position = QPointF(100, 100)
        
    def set_pattern(self, template, params):
        """Устанавливает текущий шаблон для размещения"""
        self.current_pattern = template
        self.current_params = params
        
    def mouse_press(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Проверяем, кликнули ли на существующий шаблон
            clicked_pattern = self.find_pattern_at_position(pos)
            
            if clicked_pattern:
                # Начинаем перетаскивание
                self.selected_pattern = clicked_pattern
                self.dragging = True
                self.drag_offset = pos - clicked_pattern['position']
            elif self.current_pattern:
                # Размещаем новый шаблон
                self.place_pattern(pos, canvas)
                
    def mouse_move(self, event, canvas):
        pos = canvas.mapToScene(event.pos())
        
        if self.dragging and self.selected_pattern:
            # Перемещаем выбранный шаблон
            new_position = pos - self.drag_offset
            self.move_pattern(self.selected_pattern, new_position, canvas)
            
    def mouse_release(self, event, canvas):
        self.dragging = False
        
    def place_pattern(self, position, canvas):
        """Размещает шаблон на холсте"""
        if not self.current_pattern:
            return
            
        # Генерируем путь шаблона
        path = self.current_pattern.generate_path(**self.current_params)
        
        # Создаем графический элемент
        pen = QPen(QColor(0, 0, 0), 2)
        brush = QBrush(QColor(200, 220, 255, 100))  # Полупрозрачная заливка
        
        path_item = canvas.scene.addPath(path, pen, brush)
        path_item.setPos(position)
        path_item.setFlag(path_item.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Сохраняем информацию о шаблоне
        pattern_data = {
            'template': self.current_pattern,
            'params': self.current_params.copy(),
            'position': position,
            'path_item': path_item
        }
        
        self.placed_patterns.append(pattern_data)
        
    def move_pattern(self, pattern_data, new_position, canvas):
        """Перемещает шаблон на новую позицию"""
        pattern_data['position'] = new_position
        pattern_data['path_item'].setPos(new_position)
        canvas.viewport().update()
        
    def find_pattern_at_position(self, pos):
        """Находит шаблон в указанной позиции"""
        for pattern_data in self.placed_patterns:
            path_item = pattern_data['path_item']
            item_pos = path_item.pos()
            
            # Проверяем, находится ли точка внутри bounding box
            bounds = path_item.boundingRect()
            local_pos = pos - item_pos
            
            if bounds.contains(local_pos):
                return pattern_data
                
        return None
        
    def delete_selected_pattern(self, canvas):
        """Удаляет выбранный шаблон"""
        if self.selected_pattern:
            canvas.scene.removeItem(self.selected_pattern['path_item'])
            self.placed_patterns.remove(self.selected_pattern)
            self.selected_pattern = None
            canvas.viewport().update()
            
    def clear_all_patterns(self, canvas):
        """Удаляет все шаблоны"""
        for pattern_data in self.placed_patterns:
            canvas.scene.removeItem(pattern_data['path_item'])
        self.placed_patterns = []
        self.selected_pattern = None
        canvas.viewport().update()
        
    def get_cursor(self):
        return Qt.CursorShape.ArrowCursor
