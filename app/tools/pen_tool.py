# app/tools/pen_tool.py
from PyQt6.QtCore import Qt
from .base_tool import Tool

class PenTool(Tool):
    def __init__(self):
        self.last_point = None
        
    def mouse_press(self, event, canvas):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = canvas.mapToScene(event.pos())
            
    def mouse_move(self, event, canvas):
        if self.last_point:
            current_point = canvas.mapToScene(event.pos())
            pen = canvas.get_current_pen()
            canvas.scene.addLine(
                self.last_point.x(), self.last_point.y(),
                current_point.x(), current_point.y(),
                pen
            )
            self.last_point = current_point
            
    def mouse_release(self, event, canvas):
        self.last_point = None
        
    def get_cursor(self):
        return Qt.CursorShape.CrossCursor