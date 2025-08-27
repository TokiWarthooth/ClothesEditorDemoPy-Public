# app/tools/ellipse_tool.py
from .base_tool import Tool
from PyQt6.QtCore import Qt

class EllipseTool(Tool):
    def mouse_press(self, event, canvas):
        print("Ellipse tool activated")
        
    def get_cursor(self):
        return Qt.CursorShape.CrossCursor