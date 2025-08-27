# app/tools/select_tool.py
from .base_tool import Tool
from PyQt6.QtCore import Qt

class SelectTool(Tool):
    def mouse_press(self, event, canvas):
        print("Select tool activated")
        
    def get_cursor(self):
        return Qt.CursorShape.ArrowCursor