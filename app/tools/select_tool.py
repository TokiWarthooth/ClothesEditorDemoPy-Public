from .base_tool import Tool
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView


class SelectTool(Tool):
    # Сигнализирует canvas передавать события напрямую в Qt scene
    use_scene_events = True

    def get_cursor(self):
        return Qt.CursorShape.ArrowCursor
