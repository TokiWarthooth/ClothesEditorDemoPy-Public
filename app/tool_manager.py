# app/tool_manager.py
from PyQt6.QtGui import QAction
from .tools import PenTool, SelectTool, LineTool, RectangleTool, EllipseTool, BezierTool
from .tools.pattern_tool import PatternTool

class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.tools = {
            "select": SelectTool(),
            "pen": PenTool(),
            "line": LineTool(),
            "rectangle": RectangleTool(),
            "ellipse": EllipseTool(),
            "bezier": BezierTool(),
            "pattern": PatternTool()
        }
        self.current_tool = None
        
    def get_tool_actions(self):
        actions = {}
        for tool_name, tool in self.tools.items():
            action = QAction(tool_name.capitalize(), self.canvas)
            action.triggered.connect(lambda checked, t=tool: self.set_tool(t))
            actions[tool_name] = action
        return actions
    
    def set_tool(self, tool):
        self.current_tool = tool
        self.canvas.set_tool(tool)
        # Можно добавить смену курсора
        self.canvas.setCursor(tool.get_cursor())

         # Уведомляем главное окно о смене инструмента
        if hasattr(self.canvas.parent(), 'on_tool_changed'):
            self.canvas.parent().on_tool_changed(tool)
    
    def get_pattern_tool(self):
        """Возвращает инструмент Pattern"""
        return self.tools.get("pattern")