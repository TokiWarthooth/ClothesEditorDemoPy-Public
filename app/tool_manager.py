# app/tool_manager.py
from PyQt6.QtGui import QAction
from .tools import SelectTool, TextTool, GrainlineTool
from .tools.pattern_tool import PatternTool

class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.tools = {
            "select": SelectTool(),
            "pattern": PatternTool(),
            "text": TextTool(),
            "grainline": GrainlineTool()
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
        if hasattr(self.canvas.window(), 'on_tool_changed'):
            self.canvas.window().on_tool_changed(tool)
    
    def get_pattern_tool(self):
        """Возвращает инструмент Pattern"""
        return self.tools.get("pattern")

    def get_text_tool(self):
        return self.tools.get("text")

    def get_grainline_tool(self):
        return self.tools.get("grainline")