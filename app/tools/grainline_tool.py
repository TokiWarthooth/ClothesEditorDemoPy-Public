# app/tools/grainline_tool.py
import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem
from .base_tool import Tool


def _build_grainline_path(start, end, head_size=12, head_angle_deg=28):
    """Линия со стрелками-«крыльями» на обоих концах (нотация долевой нити)."""
    path = QPainterPath()
    path.moveTo(start)
    path.lineTo(end)

    dx, dy = end.x() - start.x(), end.y() - start.y()
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return path
    ux, uy = dx / length, dy / length
    angle = math.radians(head_angle_deg)

    def add_head(tip, direction_x, direction_y):
        for sign in (-1, 1):
            a = math.atan2(direction_y, direction_x) + sign * angle
            wing = QPointF(tip.x() - math.cos(a) * head_size,
                           tip.y() - math.sin(a) * head_size)
            path.moveTo(tip)
            path.lineTo(wing)

    add_head(end, ux, uy)
    add_head(start, -ux, -uy)
    return path


class GrainlineTool(Tool):
    """Стрелка направления долевой нити: клик-клик задаёт начало и конец."""

    def __init__(self):
        self.start_point = None
        self.preview_item = None
        self.pen_color = QColor(40, 40, 40)
        self.pen_width = 1.5

    def mouse_press(self, event, canvas):
        if event.button() == Qt.MouseButton.RightButton:
            self.cancel_operation(canvas)
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = canvas.mapToScene(event.pos())
        if self.start_point is None:
            self.start_point = pos
        else:
            self.finish_arrow(self.start_point, pos, canvas)
            self.start_point = None
            self._clear_preview(canvas)

    def mouse_move(self, event, canvas):
        if self.start_point is None:
            return
        pos = canvas.mapToScene(event.pos())
        self._update_preview(self.start_point, pos, canvas)

    def _update_preview(self, start, end, canvas):
        path = _build_grainline_path(start, end)
        pen = QPen(QColor(120, 120, 120, 160), 1, Qt.PenStyle.DashLine)
        if self.preview_item:
            canvas.scene.removeItem(self.preview_item)
        self.preview_item = canvas.scene.addPath(path, pen)

    def _clear_preview(self, canvas):
        if self.preview_item:
            canvas.scene.removeItem(self.preview_item)
            self.preview_item = None

    def finish_arrow(self, start, end, canvas):
        path = _build_grainline_path(start, end)
        pen = QPen(self.pen_color, self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        item = QGraphicsPathItem(path)
        item.setPen(pen)
        item.setFlags(
            item.GraphicsItemFlag.ItemIsSelectable |
            item.GraphicsItemFlag.ItemIsMovable
        )

        from ..commands import AddItemCommand
        canvas.undo_stack.push(AddItemCommand(canvas.scene, item, "Add grainline arrow"))

    def cancel_operation(self, canvas):
        self.start_point = None
        self._clear_preview(canvas)

    def reset(self, canvas=None):
        self.start_point = None
        if canvas:
            self._clear_preview(canvas)

    def get_cursor(self):
        return Qt.CursorShape.CrossCursor
