# app/tools/polygon_tool.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush, QPainterPath
from PyQt6.QtWidgets import QApplication
from .base_tool import Tool
from .pattern_item import PatternPieceItem

CLOSE_RADIUS_PX = 10       # экранных пикселей — клик в этом радиусе от старта замыкает фигуру
MIN_POINTS_TO_CLOSE = 3    # меньше — не фигура, а линия


class PolygonTool(Tool):
    """Рисование собственной фигуры точками, соединёнными прямыми.

    Клик — добавить вершину (с зажатым Shift — с привязкой к клеткам сетки,
    как и при перетаскивании объектов). Клик рядом со стартовой точкой (или
    Enter) — замкнуть контур и превратить его в новую фигуру — обычный
    PatternPieceItem, со всеми хендлами ресайза, припусками на швы и т.д.
    ПКМ/Esc — отменить построение.
    """

    def __init__(self):
        self.points = []
        self.preview_item = None

    def _snap(self, pos, canvas):
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
            g = canvas.grid_size
            return QPointF(round(pos.x() / g) * g, round(pos.y() / g) * g)
        return pos

    def _close_radius(self, canvas):
        scale = canvas.transform().m11() or 1.0
        return CLOSE_RADIUS_PX / scale

    def mouse_press(self, event, canvas):
        if event.button() == Qt.MouseButton.RightButton:
            self.cancel_operation(canvas)
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return

        pos = self._snap(canvas.mapToScene(event.pos()), canvas)

        if len(self.points) >= MIN_POINTS_TO_CLOSE:
            start = self.points[0]
            dist = ((pos.x() - start.x()) ** 2 + (pos.y() - start.y()) ** 2) ** 0.5
            if dist <= self._close_radius(canvas):
                self._finish(canvas)
                return

        self.points.append(pos)
        self._update_preview(canvas, pos)

    def mouse_move(self, event, canvas):
        if not self.points:
            return
        pos = self._snap(canvas.mapToScene(event.pos()), canvas)
        self._update_preview(canvas, pos)

    def _update_preview(self, canvas, cursor_pos):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        path.lineTo(cursor_pos)

        # Маркер стартовой точки — показывает, куда кликнуть, чтобы замкнуть контур
        if len(self.points) >= MIN_POINTS_TO_CLOSE:
            r = self._close_radius(canvas)
            path.addEllipse(self.points[0], r, r)

        pen = QPen(QColor(70, 130, 220), 1.5, Qt.PenStyle.DashLine)
        self._clear_preview(canvas)
        self.preview_item = canvas.scene.addPath(path, pen)

    def _clear_preview(self, canvas):
        if self.preview_item:
            canvas.scene.removeItem(self.preview_item)
            self.preview_item = None

    def _finish(self, canvas):
        if len(self.points) < MIN_POINTS_TO_CLOSE:
            self.cancel_operation(canvas)
            return

        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        path.closeSubpath()

        pen = QPen(QColor(0, 0, 0), 2)
        pen.setCosmetic(True)
        brush = QBrush(QColor(200, 220, 255, 100))

        item = PatternPieceItem(path, vertices=self.points)
        item.setPen(pen)
        item.setBrush(brush)

        from ..core.commands import AddItemCommand
        canvas.undo_stack.push(AddItemCommand(canvas.scene, item, "Add custom shape"))

        self._reset(canvas)

    def cancel_operation(self, canvas):
        self._reset(canvas)

    def finish_operation(self, canvas):
        self._finish(canvas)

    def _reset(self, canvas):
        self.points = []
        self._clear_preview(canvas)

    def reset(self, canvas=None):
        self.points = []
        if canvas:
            self._clear_preview(canvas)

    def get_cursor(self):
        return Qt.CursorShape.CrossCursor
