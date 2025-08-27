from PyQt6.QtGui import QAction, QPen
from PyQt6.QtCore import Qt

class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.tools = {
            "select": SelectTool(),
            "pen": PenTool(),
            "line": LineTool(),
            "rectangle": RectangleTool(),
            "ellipse": EllipseTool(),
            "bezier": BezierTool()
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

# Базовый класс для инструментов
class Tool:
    def mouse_press(self, event, canvas):
        pass
        
    def mouse_move(self, event, canvas):
        pass
        
    def mouse_release(self, event, canvas):
        pass

# Конкретные реализации инструментов
class SelectTool(Tool):
    def mouse_press(self, event, canvas):
        print("Select tool activated")

class PenTool(Tool):
    def __init__(self):
        self.last_point = None
        
    def mouse_press(self, event, canvas):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = canvas.mapToScene(event.pos())
            
    def mouse_move(self, event, canvas):
        if self.last_point:
            current_point = canvas.mapToScene(event.pos())
            # Используем метод get_current_pen из Canvas
            pen = canvas.get_current_pen()
            canvas.scene.addLine(
                self.last_point.x(), self.last_point.y(),
                current_point.x(), current_point.y(),
                pen
            )
            self.last_point = current_point
            
    def mouse_release(self, event, canvas):
        self.last_point = None

class LineTool(Tool):
    def mouse_press(self, event, canvas):
        print("Line tool activated")

class RectangleTool(Tool):
    def mouse_press(self, event, canvas):
        print("Rectangle tool activated")

class EllipseTool(Tool):
    def mouse_press(self, event, canvas):
        print("Ellipse tool activated")

class BezierTool(Tool):
    def mouse_press(self, event, canvas):
        print("Bezier tool activated")