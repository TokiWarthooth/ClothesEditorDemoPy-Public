from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QDoubleSpinBox, QPushButton, QGraphicsPathItem)
from PyQt6.QtGui import QPainterPathStroker, QPen, QColor
from PyQt6.QtCore import Qt

# Тег для идентификации элементов припуска
_SEAM_TAG = "seam_allowance"
_SEAM_KEY  = 0          # ключ для item.setData()

PX_PER_MM = 96 / 25.4  # 3.7795 px/мм при 96 dpi


def _compute_seam_path(original_path, allowance_px):
    """Возвращает расширенный контур (cutting line) для заданного пути."""
    stroker = QPainterPathStroker()
    stroker.setWidth(allowance_px * 2)          # расширение в обе стороны
    stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    stroker.setCapStyle(Qt.PenCapStyle.SquareCap)
    stroke = stroker.createStroke(original_path)
    return original_path.united(stroke)         # внешний контур = оригинал + кольцо


class SeamAllowancePanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Seam Allowance")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        # Ширина припуска
        row = QHBoxLayout()
        row.addWidget(QLabel("Width:"))
        self.spin = QDoubleSpinBox()
        self.spin.setRange(1.0, 50.0)
        self.spin.setValue(10.0)
        self.spin.setSuffix(" mm")
        self.spin.setSingleStep(1.0)
        self.spin.setDecimals(1)
        row.addWidget(self.spin)
        layout.addLayout(row)

        # Кнопка добавить
        btn_add = QPushButton("Add to Selected")
        btn_add.setToolTip("Выберите детали выкройки (Select), затем нажмите")
        btn_add.clicked.connect(self._apply)
        layout.addWidget(btn_add)

        # Кнопка удалить все припуски
        btn_remove = QPushButton("Remove All Seam Lines")
        btn_remove.clicked.connect(self._remove_all)
        layout.addWidget(btn_remove)

        hint = QLabel("Tip: select pattern pieces\nwith the Select tool first.")
        hint.setStyleSheet("color: #888; font-size: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

    def _apply(self):
        from .commands import AddItemCommand

        items = [i for i in self.canvas.scene.selectedItems()
                 if hasattr(i, 'path') and i.data(_SEAM_KEY) != _SEAM_TAG]
        if not items:
            return

        allowance_px = self.spin.value() * PX_PER_MM

        for item in items:
            seam_path = _compute_seam_path(item.path(), allowance_px)

            pen = QPen(QColor(210, 50, 50), 1.5, Qt.PenStyle.DashLine)
            seam_item = QGraphicsPathItem(seam_path)
            seam_item.setPen(pen)
            seam_item.setPos(item.pos())
            seam_item.setTransform(item.transform())
            seam_item.setData(_SEAM_KEY, _SEAM_TAG)   # помечаем как припуск
            seam_item.setFlags(
                seam_item.GraphicsItemFlag.ItemIsSelectable |
                seam_item.GraphicsItemFlag.ItemIsMovable
            )

            self.canvas.undo_stack.push(
                AddItemCommand(self.canvas.scene, seam_item, "Add seam allowance")
            )

    def _remove_all(self):
        from .commands import RemoveItemsCommand
        seam_items = [i for i in self.canvas.scene.items()
                      if i.data(_SEAM_KEY) == _SEAM_TAG]
        if seam_items:
            self.canvas.undo_stack.push(
                RemoveItemsCommand(self.canvas.scene, seam_items, "Remove seam lines")
            )
