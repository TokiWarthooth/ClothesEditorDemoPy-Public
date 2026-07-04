# app/tools/pattern_item.py
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QTransform, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem

HANDLE_SIZE = 10
MIN_SCALE = 0.1


class PatternPieceItem(QGraphicsPathItem):
    """Деталь выкройки на холсте с угловыми хендлами для изменения размера.

    Ресайз реализован через QTransform (масштаб от опорного угла), а не
    пересборкой пути по параметрам шаблона — у разных шаблонов разные имена
    параметров (width/height, waist_width/hip_width и т.д.), а трансформ
    работает одинаково для любой формы.
    """

    def __init__(self, path):
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

    def _handle_at(self, local_pos):
        for name, rect in self._handle_rects().items():
            if rect.contains(local_pos):
                return name
        return None

    def hoverMoveEvent(self, event):
        handle = self._handle_at(event.pos()) if self.isSelected() else None
        if handle in ('tl', 'br'):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif handle in ('tr', 'bl'):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.unsetCursor()
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        handle = self._handle_at(event.pos()) if self.isSelected() else None
        if handle:
            self._active_handle = handle
            self._drag_base_transform = QTransform(self.transform())
            self._drag_old_transform = QTransform(self.transform())
            self._drag_rect = self.path().boundingRect()
            event.accept()
            return
        self._active_handle = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._active_handle:
            self._preview_resize(event)
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
                    from ..commands import TransformCommand
                    canvas.undo_stack.push(
                        TransformCommand(self, old_transform, new_transform, "Resize pattern piece")
                    )
                else:
                    self.setTransform(new_transform)
            event.accept()
            return
        super().mouseReleaseEvent(event)

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
