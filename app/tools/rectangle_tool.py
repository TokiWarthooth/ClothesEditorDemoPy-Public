# app/tools/rectangle_tool.py
from .base_tool import Tool
from PyQt6.QtCore import Qt

class RectangleTool(Tool):
    def mouse_press(self, event, canvas):
        print("Rectangle tool activated")
        
    def get_cursor(self):
        return Qt.CursorShape.CrossCursor