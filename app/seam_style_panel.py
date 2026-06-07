import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QDoubleSpinBox, QPushButton,
                             QGraphicsPathItem)
from PyQt6.QtGui import QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF

# Тег для маркировки оверлеев стиля шва
_STYLE_TAG = "seam_style"
_STYLE_KEY = 1


def _make_zigzag_path(source_path, amplitude, step):
    """Зигзаг вдоль исходного пути: семплируем точки, чередуем смещение по нормали."""
    total = source_path.length()
    if total < 1:
        return QPainterPath(source_path)

    result = QPainterPath()
    step_t = max(step / total, 0.001)
    flip = 1
    first = True
    t = 0.0
    while t <= 1.0001:
        tc = min(t, 1.0)
        pt = source_path.pointAtPercent(tc)
        angle = math.radians(source_path.angleAtPercent(tc) + 90)
        dest = QPointF(pt.x() + math.cos(angle) * amplitude * flip,
                       pt.y() - math.sin(angle) * amplitude * flip)
        if first:
            result.moveTo(dest)
            first = False
        else:
            result.lineTo(dest)
        flip = -flip
        t += step_t
    return result


def _make_overlock_path(source_path, size, step):
    """Оверлок: короткие штрихи перпендикулярно линии шва (классическая нотация)."""
    total = source_path.length()
    if total < 1:
        return QPainterPath(source_path)

    result = QPainterPath()
    step_t = max(step / total, 0.001)
    t = 0.0
    while t <= 1.0001:
        tc = min(t, 1.0)
        pt = source_path.pointAtPercent(tc)
        angle = math.radians(source_path.angleAtPercent(tc) + 60)
        end = QPointF(pt.x() + math.cos(angle) * size,
                      pt.y() - math.sin(angle) * size)
        result.moveTo(pt)
        result.lineTo(end)
        t += step_t
    return result


class SeamStylePanel(QWidget):
    STYLES = ["Straight", "Zigzag", "Overlock"]

    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Seam Stitch Style")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Type:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(self.STYLES)
        row1.addWidget(self.style_combo)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Size:"))
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(2.0, 30.0)
        self.size_spin.setValue(6.0)
        self.size_spin.setSuffix(" px")
        row2.addWidget(self.size_spin)
        layout.addLayout(row2)

        btn_apply = QPushButton("Apply to Selected")
        btn_apply.setToolTip("Выберите линию швов (Select), затем нажмите")
        btn_apply.clicked.connect(self._apply)
        layout.addWidget(btn_apply)

        btn_remove = QPushButton("Remove Style Overlays")
        btn_remove.clicked.connect(self._remove_all)
        layout.addWidget(btn_remove)

        hint = QLabel("Straight меняет стиль самой линии.\n"
                      "Zigzag/Overlock добавляют поверх неё условную отметку шва.")
        hint.setStyleSheet("color: #888; font-size: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

    def _apply(self):
        from .commands import AddItemCommand, ChangePenCommand

        items = [i for i in self.canvas.scene.selectedItems()
                 if hasattr(i, 'path') and i.data(_STYLE_KEY) != _STYLE_TAG]
        if not items:
            return

        style = self.style_combo.currentText()
        size = self.size_spin.value()

        for item in items:
            if style == "Straight":
                old_pen = item.pen()
                new_pen = QPen(old_pen)
                new_pen.setStyle(Qt.PenStyle.SolidLine)
                self.canvas.undo_stack.push(
                    ChangePenCommand(item, old_pen, new_pen, "Set straight stitch")
                )
                continue

            if style == "Zigzag":
                overlay_path = _make_zigzag_path(item.path(), amplitude=size, step=size * 1.5)
                color = QColor(60, 120, 220)
            else:  # Overlock
                overlay_path = _make_overlock_path(item.path(), size=size, step=size * 1.5)
                color = QColor(220, 130, 30)

            overlay = QGraphicsPathItem(overlay_path)
            overlay.setPen(QPen(color, 1.5))
            overlay.setPos(item.pos())
            overlay.setTransform(item.transform())
            overlay.setData(_STYLE_KEY, _STYLE_TAG)
            overlay.setFlags(
                overlay.GraphicsItemFlag.ItemIsSelectable |
                overlay.GraphicsItemFlag.ItemIsMovable
            )
            self.canvas.undo_stack.push(
                AddItemCommand(self.canvas.scene, overlay, f"Add {style.lower()} stitch mark")
            )

    def _remove_all(self):
        from .commands import RemoveItemsCommand
        overlays = [i for i in self.canvas.scene.items()
                    if i.data(_STYLE_KEY) == _STYLE_TAG]
        if overlays:
            self.canvas.undo_stack.push(
                RemoveItemsCommand(self.canvas.scene, overlays, "Remove stitch marks")
            )
