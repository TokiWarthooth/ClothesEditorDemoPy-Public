# app/tools/base_tool.py
from PyQt6.QtCore import Qt

class Tool:
    def mouse_press(self, event, canvas):
        pass
        
    def mouse_move(self, event, canvas):
        pass
        
    def mouse_release(self, event, canvas):
        pass
        
    def get_icon(self):
        """Возвращает иконку инструмента (можно реализовать позже)"""
        return None
        
    def get_cursor(self):
        """Возвращает курсор для инструмента (можно реализовать позже)"""
        return Qt.CursorShape.ArrowCursor