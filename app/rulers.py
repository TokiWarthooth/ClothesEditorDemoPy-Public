import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPointF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

RULER_SIZE = 22  # px — ширина вертикальной и высота горизонтальной линейки


class _RulerBase(QWidget):
    def __init__(self, canvas, measurements, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.measurements = measurements
        self._cursor_x = None   # позиция курсора в координатах сцены
        self._cursor_y = None

    def update_cursor(self, scene_x, scene_y):
        self._cursor_x = scene_x
        self._cursor_y = scene_y
        self.update()

    def _to_widget(self, scene_x, scene_y):
        """Сцена → координаты этого виджета."""
        vp_pt = self.canvas.mapFromScene(QPointF(scene_x, scene_y))
        return self.canvas.viewport().mapTo(self.canvas, vp_pt)

    def _format_label(self, scene_value, decimals):
        v = self.measurements.px_to_unit(scene_value)
        if self.measurements.unit == "px":
            return str(int(round(v)))
        return str(int(round(v))) if decimals == 0 else f"{v:.{decimals}f}"


class HorizontalRuler(_RulerBase):
    def __init__(self, canvas, measurements, parent=None):
        super().__init__(canvas, measurements, parent)
        self.setFixedHeight(RULER_SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(242, 242, 242))
        painter.setPen(QPen(QColor(190, 190, 190)))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        vp = self.canvas.viewport()
        scene_left  = self.canvas.mapToScene(vp.rect().topLeft()).x()
        scene_right = self.canvas.mapToScene(vp.rect().topRight()).x()
        visible = scene_right - scene_left
        if visible <= 0:
            return

        step_px, decimals = self.measurements.nice_step(visible)
        if step_px <= 0:
            return

        minor_step = step_px / 5
        h = self.height()

        # Малые деления
        painter.setPen(QPen(QColor(190, 190, 190)))
        x = math.floor(scene_left / minor_step) * minor_step
        while x <= scene_right:
            rx = self._to_widget(x, 0).x()
            if 0 <= rx <= self.width():
                painter.drawLine(rx, h - 5, rx, h - 1)
            x += minor_step

        # Крупные деления + подписи
        painter.setFont(QFont("Arial", 6))
        painter.setPen(QPen(QColor(70, 70, 70)))
        x = math.floor(scene_left / step_px) * step_px
        while x <= scene_right + step_px:
            rx = self._to_widget(x, 0).x()
            if 0 <= rx <= self.width():
                painter.drawLine(rx, 0, rx, h - 1)
                painter.drawText(rx + 2, h - 7, self._format_label(x, decimals))
            x += step_px

        # Индикатор курсора
        if self._cursor_x is not None:
            cx = self._to_widget(self._cursor_x, 0).x()
            painter.setPen(QPen(QColor(210, 60, 60), 1))
            painter.drawLine(cx, 0, cx, h)


class VerticalRuler(_RulerBase):
    def __init__(self, canvas, measurements, parent=None):
        super().__init__(canvas, measurements, parent)
        self.setFixedWidth(RULER_SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(242, 242, 242))
        painter.setPen(QPen(QColor(190, 190, 190)))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        vp = self.canvas.viewport()
        scene_top    = self.canvas.mapToScene(vp.rect().topLeft()).y()
        scene_bottom = self.canvas.mapToScene(vp.rect().bottomLeft()).y()
        visible = scene_bottom - scene_top
        if visible <= 0:
            return

        step_px, decimals = self.measurements.nice_step(visible)
        if step_px <= 0:
            return

        minor_step = step_px / 5
        w = self.width()

        # Малые деления
        painter.setPen(QPen(QColor(190, 190, 190)))
        y = math.floor(scene_top / minor_step) * minor_step
        while y <= scene_bottom:
            ry = self._to_widget(0, y).y()
            if 0 <= ry <= self.height():
                painter.drawLine(w - 5, ry, w - 1, ry)
            y += minor_step

        # Крупные деления + подписи (повёрнутые)
        painter.setFont(QFont("Arial", 6))
        painter.setPen(QPen(QColor(70, 70, 70)))
        y = math.floor(scene_top / step_px) * step_px
        while y <= scene_bottom + step_px:
            ry = self._to_widget(0, y).y()
            if 0 <= ry <= self.height():
                painter.drawLine(0, ry, w - 1, ry)
                label = self._format_label(y, decimals)
                painter.save()
                painter.translate(w - 3, ry - 2)
                painter.rotate(-90)
                painter.drawText(0, 0, label)
                painter.restore()
            y += step_px

        # Индикатор курсора
        if self._cursor_y is not None:
            cy = self._to_widget(0, self._cursor_y).y()
            painter.setPen(QPen(QColor(210, 60, 60), 1))
            painter.drawLine(0, cy, w, cy)
