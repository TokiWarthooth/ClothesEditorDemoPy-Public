# app/tools/pattern_item.py
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QTransform, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from .graphics_items import GridSnapMixin

HANDLE_SIZE = 10
EDGE_HANDLE_SIZE = 8
MIN_SCALE = 0.1
# Порог (в локальных координатах пути) — если оттянутую точку ребра вернули
# ближе этого расстояния к прямой середине ребра, ребро "распрямляется"
# обратно (control=None), а не остаётся кривой почти незаметной кривизны.
EDGE_STRAIGHTEN_THRESHOLD = 4


class PatternPieceItem(GridSnapMixin, QGraphicsPathItem):
    """Деталь выкройки на холсте с угловыми хендлами для изменения размера.

    Ресайз реализован через QTransform (масштаб от опорного угла), а не
    пересборкой пути по параметрам шаблона — у разных шаблонов разные имена
    параметров (width/height, waist_width/hip_width и т.д.), а трансформ
    работает одинаково для любой формы.

    Если при создании передан `vertices` (список вершин контура в тех же
    локальных координатах, что и path — так делает PolygonTool), деталь
    дополнительно даёт хендлы на серединах рёбер: перетаскивание такого
    хендла выгибает соответствующее ребро в квадратичную кривую Безье, а
    сами вершины по краям ребра остаются на месте. Это нужно, например, для
    выгибания прямого края рукава в пройму. Для деталей без vertices (пути
    шаблонов) эта возможность недоступна — там нет однозначного разбиения
    пути на прямые рёбра.
    """

    def __init__(self, path, vertices=None):
        super().__init__(path)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        self.setAcceptHoverEvents(True)
        self._active_handle = None
        self._drag_base_transform = None
        self._drag_old_transform = None
        self._drag_rect = None

        self._vertices = list(vertices) if vertices else None
        self._edge_controls = [None] * len(self._vertices) if self._vertices else None
        self._active_edge = None
        self._drag_edge_old_controls = None
        self._drag_edge_p0 = None
        self._drag_edge_p1 = None
        if self._vertices:
            self._rebuild_path()

    def _handle_points(self):
        rect = self.path().boundingRect()
        return {
            'tl': rect.topLeft(),
            'tr': rect.topRight(),
            'bl': rect.bottomLeft(),
            'br': rect.bottomRight(),
        }

    def _handle_rects(self):
        # HANDLE_SIZE — желаемый размер квадратика в экранных пикселях.
        # paint()/hit-testing работают в локальных координатах пути, которые
        # затем домножаются на self.transform() — если рисовать квадратик
        # фиксированного РАЗМЕРА В ЛОКАЛЬНЫХ единицах, при несимметричном
        # масштабе (после ресайза) он сам исказится вместе с фигурой. Поэтому
        # делим желаемый размер на текущий масштаб по каждой оси, чтобы после
        # применения transform() квадратик остался квадратиком.
        t = self.transform()
        sx = abs(t.m11()) or 1.0
        sy = abs(t.m22()) or 1.0
        hw = HANDLE_SIZE / sx / 2
        hh = HANDLE_SIZE / sy / 2
        return {name: QRectF(p.x() - hw, p.y() - hh, hw * 2, hh * 2)
                for name, p in self._handle_points().items()}

    def _rebuild_path(self):
        n = len(self._vertices)
        path = QPainterPath(self._vertices[0])
        for i in range(n):
            p1 = self._vertices[(i + 1) % n]
            control = self._edge_controls[i]
            if control is None:
                path.lineTo(p1)
            else:
                path.quadTo(control, p1)
        path.closeSubpath()
        self.setPath(path)

    def _edge_midpoints(self):
        # Точка на середине ребра (t=0.5) — для прямого ребра это обычная
        # середина отрезка, для уже выгнутого — точка на кривой Безье. Именно
        # эта точка визуально становится хендлом, который тянет пользователь,
        # поэтому формула перетаскивания в _preview_edge_curve — её обращение.
        if not self._vertices:
            return {}
        n = len(self._vertices)
        points = {}
        for i in range(n):
            p0 = self._vertices[i]
            p1 = self._vertices[(i + 1) % n]
            control = self._edge_controls[i]
            if control is None:
                points[i] = QPointF((p0.x() + p1.x()) / 2, (p0.y() + p1.y()) / 2)
            else:
                points[i] = QPointF(
                    0.25 * p0.x() + 0.5 * control.x() + 0.25 * p1.x(),
                    0.25 * p0.y() + 0.5 * control.y() + 0.25 * p1.y(),
                )
        return points

    def _edge_handle_rects(self):
        if not self._vertices:
            return {}
        t = self.transform()
        sx = abs(t.m11()) or 1.0
        sy = abs(t.m22()) or 1.0
        hw = EDGE_HANDLE_SIZE / sx / 2
        hh = EDGE_HANDLE_SIZE / sy / 2
        return {i: QRectF(p.x() - hw, p.y() - hh, hw * 2, hh * 2)
                for i, p in self._edge_midpoints().items()}

    def set_edge_control(self, index, control):
        self._edge_controls[index] = control
        self._rebuild_path()

    def boundingRect(self):
        rect = super().boundingRect()
        t = self.transform()
        sx = abs(t.m11()) or 1.0
        sy = abs(t.m22()) or 1.0
        pad_x = HANDLE_SIZE / sx
        pad_y = HANDLE_SIZE / sy
        return rect.adjusted(-pad_x, -pad_y, pad_x, pad_y)

    def shape(self):
        # По умолчанию Qt проверяет попадание клика по контуру/заливке пути
        # (super().shape()), а хендлы стоят по углам bounding box — у кривых
        # фигур (рукав, воротник) эти углы обычно лежат далеко за пределами
        # самого контура. Без этого клик по квадратику "проваливается" мимо
        # объекта, вместо ресайза начинается rubber-band выделение, и деталь
        # выглядит так, будто пропала.
        base = super().shape()
        if not self.isSelected():
            return base
        combined = QPainterPath(base)
        for rect in self._handle_rects().values():
            handle_path = QPainterPath()
            handle_path.addRect(rect)
            combined = combined.united(handle_path)
        for rect in self._edge_handle_rects().values():
            handle_path = QPainterPath()
            handle_path.addRect(rect)
            combined = combined.united(handle_path)
        return combined

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            outline_pen = QPen(QColor(30, 120, 255), 1, Qt.PenStyle.DashLine)
            outline_pen.setCosmetic(True)  # толщина рамки не зависит от масштаба фигуры
            rect = self.path().boundingRect()
            painter.setPen(outline_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            handle_pen = QPen(QColor(30, 120, 255), 1)
            handle_pen.setCosmetic(True)
            painter.setPen(handle_pen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            for handle_rect in self._handle_rects().values():
                painter.drawRect(handle_rect)

            if self._vertices:
                edge_handle_pen = QPen(QColor(255, 140, 0), 1)
                edge_handle_pen.setCosmetic(True)
                painter.setPen(edge_handle_pen)
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                for edge_rect in self._edge_handle_rects().values():
                    painter.drawEllipse(edge_rect)

    def _handle_at(self, local_pos):
        for name, rect in self._handle_rects().items():
            if rect.contains(local_pos):
                return ('corner', name)
        for index, rect in self._edge_handle_rects().items():
            if rect.contains(local_pos):
                return ('edge', index)
        return None

    def hoverMoveEvent(self, event):
        handle = self._handle_at(event.pos()) if self.isSelected() else None
        kind = handle[0] if handle else None
        name = handle[1] if handle else None
        if kind == 'corner' and name in ('tl', 'br'):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif kind == 'corner' and name in ('tr', 'bl'):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif kind == 'edge':
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.unsetCursor()
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        handle = self._handle_at(event.pos()) if self.isSelected() else None
        if handle and handle[0] == 'corner':
            self._active_handle = handle[1]
            self._drag_base_transform = QTransform(self.transform())
            self._drag_old_transform = QTransform(self.transform())
            self._drag_rect = self.path().boundingRect()
            event.accept()
            return
        if handle and handle[0] == 'edge':
            index = handle[1]
            n = len(self._vertices)
            self._active_edge = index
            self._drag_base_transform = QTransform(self.transform())
            self._drag_edge_old_controls = list(self._edge_controls)
            self._drag_edge_p0 = self._vertices[index]
            self._drag_edge_p1 = self._vertices[(index + 1) % n]
            event.accept()
            return
        self._active_handle = None
        self._active_edge = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._active_handle:
            self._preview_resize(event)
            event.accept()
            return
        if self._active_edge is not None:
            self._preview_edge_curve(event)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._active_handle:
            self._active_handle = None
            new_transform = QTransform(self.transform())
            old_transform = self._drag_old_transform
            if new_transform != old_transform:
                self.setTransform(old_transform)
                scene = self.scene()
                canvas = scene.views()[0] if scene and scene.views() else None
                if canvas is not None:
                    from ..core.commands import TransformCommand
                    canvas.undo_stack.push(
                        TransformCommand(self, old_transform, new_transform, "Resize pattern piece")
                    )
                else:
                    self.setTransform(new_transform)
            event.accept()
            return
        if self._active_edge is not None:
            index = self._active_edge
            old_control = self._drag_edge_old_controls[index]
            new_control = self._edge_controls[index]
            self._active_edge = None
            if new_control != old_control:
                self._edge_controls[index] = old_control
                self._rebuild_path()
                scene = self.scene()
                canvas = scene.views()[0] if scene and scene.views() else None
                if canvas is not None:
                    from ..core.commands import EdgeCurveCommand
                    canvas.undo_stack.push(
                        EdgeCurveCommand(self, index, old_control, new_control, "Curve pattern edge")
                    )
                else:
                    self.set_edge_control(index, new_control)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _preview_edge_curve(self, event):
        # Аналогично _preview_resize — координаты курсора переводим в
        # локальные через трансформацию, зафиксированную в начале драга.
        rel = event.scenePos() - self.pos()
        inverted, ok = self._drag_base_transform.inverted()
        local_pos = inverted.map(rel) if ok else rel

        p0, p1 = self._drag_edge_p0, self._drag_edge_p1
        straight_mid = QPointF((p0.x() + p1.x()) / 2, (p0.y() + p1.y()) / 2)
        dx = local_pos.x() - straight_mid.x()
        dy = local_pos.y() - straight_mid.y()
        if (dx * dx + dy * dy) ** 0.5 < EDGE_STRAIGHTEN_THRESHOLD:
            self._edge_controls[self._active_edge] = None
        else:
            # Хендл стоит на самой кривой (t=0.5, см. _edge_midpoints), значит
            # чтобы кривая прошла через точку под курсором, контрольную точку
            # квадратичной кривой находим обращением B(0.5) = .25P0+.5C+.25P1.
            self._edge_controls[self._active_edge] = QPointF(
                2 * local_pos.x() - 0.5 * (p0.x() + p1.x()),
                2 * local_pos.y() - 0.5 * (p0.y() + p1.y()),
            )
        self._rebuild_path()

    def _preview_resize(self, event):
        # Переводим позицию курсора в "локальные" координаты пути через
        # трансформацию, зафиксированную в начале драга (а не текущую,
        # которая меняется на каждом кадре) — иначе живой предпросмотр
        # уводило бы в разнос обратной связью.
        rel = event.scenePos() - self.pos()
        inverted, ok = self._drag_base_transform.inverted()
        local_pos = inverted.map(rel) if ok else rel

        rect = self._drag_rect
        handle = self._active_handle

        anchors = {'br': rect.topLeft(), 'tl': rect.bottomRight(),
                   'tr': rect.bottomLeft(), 'bl': rect.topRight()}
        corners = {'br': rect.bottomRight(), 'tl': rect.topLeft(),
                   'tr': rect.topRight(), 'bl': rect.bottomLeft()}
        anchor = anchors[handle]
        corner = corners[handle]

        dx = corner.x() - anchor.x()
        dy = corner.y() - anchor.y()
        if abs(dx) < 1e-6 or abs(dy) < 1e-6:
            return

        sx = (local_pos.x() - anchor.x()) / dx
        sy = (local_pos.y() - anchor.y()) / dy
        # Всегда положительный пол на масштаб — иначе перетаскивание угла
        # мимо противоположного (якорного) угла зеркалит фигуру. Раньше тут
        # была ветка по знаку dx/dy, но dx/dy отрицательны для tl/tr/bl просто
        # из-за системы координат Qt (не из-за направления перетаскивания),
        # поэтому та ветка ошибочно форсила отрицательный масштаб — отсюда
        # "сплющивание" на всех хендлах, кроме br.
        sx = max(sx, MIN_SCALE)
        sy = max(sy, MIN_SCALE)

        t = QTransform()
        t.translate(anchor.x(), anchor.y())
        t.scale(sx, sy)
        t.translate(-anchor.x(), -anchor.y())

        # t зажат в ИСХОДНЫХ (нетрансформированных) координатах пути, поэтому
        # его нужно применять ПЕРВЫМ, а уже поверх — базовую трансформацию,
        # накопленную с прошлых ресайзов/флипов: Qt's `A * B` означает "сначала
        # A, потом B" (проверено эмпирически), значит нужен порядок `t * base`,
        # а не `base * t`. С identity-базой (самый первый ресайз) разницы нет —
        # поэтому баг был незаметен, пока не попробовали изменить размер второй раз.
        self.setTransform(t * self._drag_base_transform)
