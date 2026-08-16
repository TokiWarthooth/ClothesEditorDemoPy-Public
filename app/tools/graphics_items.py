# app/tools/graphics_items.py
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsItem, QGraphicsPathItem, QGraphicsTextItem


class GridSnapMixin:
    """Подмешивается к перемещаемым QGraphicsItem: пока при перетаскивании
    зажат Shift, позиция объекта привязывается к клеткам сетки холста.
    Отпустили Shift — снова обычное свободное перемещение."""

    def setFlags(self, flags):
        # itemChange() получает уведомления о ItemPositionChange только если
        # выставлен ItemSendsGeometryChanges — досыпаем его при любом вызове
        # setFlags(), чтобы не нужно было помнить об этом в каждом месте,
        # где создаётся перемещаемый объект.
        super().setFlags(flags | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
                scene = self.scene()
                views = scene.views() if scene else []
                canvas = views[0] if views else None
                grid_size = getattr(canvas, 'grid_size', None)
                if grid_size:
                    return QPointF(
                        round(value.x() / grid_size) * grid_size,
                        round(value.y() / grid_size) * grid_size,
                    )
        return super().itemChange(change, value)


class SnappablePathItem(GridSnapMixin, QGraphicsPathItem):
    """QGraphicsPathItem с привязкой к сетке при зажатом Shift."""
    pass


class SnappableTextItem(GridSnapMixin, QGraphicsTextItem):
    """QGraphicsTextItem с привязкой к сетке при зажатом Shift."""
    pass
