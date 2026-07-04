# app/pattern_size_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QDoubleSpinBox, QPushButton)
from PyQt6.QtGui import QTransform
from PyQt6.QtCore import QTimer
from .measurements import MeasurementSystem
from .tools.pattern_item import PatternPieceItem

PX_PER_CM = MeasurementSystem.PX_PER_CM


class PatternSizePanel(QWidget):
    """Точный ввод ширины/высоты выбранной детали выкройки в сантиметрах."""

    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.current_item = None
        self._init_ui()
        # Calling scene.selectedItems() synchronously from inside a
        # selectionChanged handler crashes PyQt6 (reproducible even with a
        # plain QGraphicsPathItem, no custom code involved) — deferring one
        # event-loop tick via singleShot(0, ...) avoids it.
        canvas.scene.selectionChanged.connect(
            lambda: QTimer.singleShot(0, self._on_selection_changed)
        )

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Pattern Size")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        row_w = QHBoxLayout()
        row_w.addWidget(QLabel("Width:"))
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 1000.0)
        self.width_spin.setSuffix(" cm")
        self.width_spin.setDecimals(1)
        row_w.addWidget(self.width_spin)
        layout.addLayout(row_w)

        row_h = QHBoxLayout()
        row_h.addWidget(QLabel("Height:"))
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 1000.0)
        self.height_spin.setSuffix(" cm")
        self.height_spin.setDecimals(1)
        row_h.addWidget(self.height_spin)
        layout.addLayout(row_h)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply)
        layout.addWidget(self.apply_button)

        hint = QLabel("Tip: select one pattern piece\nwith the Select tool first.")
        hint.setStyleSheet("color: #888; font-size: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()
        self.setEnabled(False)

    def _on_selection_changed(self):
        items = [i for i in self.canvas.scene.selectedItems()
                 if isinstance(i, PatternPieceItem)]
        if len(items) == 1:
            self.current_item = items[0]
            self._refresh_from_item()
            self.setEnabled(True)
        else:
            self.current_item = None
            self.setEnabled(False)

    def _refresh_from_item(self):
        item = self.current_item
        rect = item.path().boundingRect()
        t = item.transform()
        width_px = rect.width() * abs(t.m11())
        height_px = rect.height() * abs(t.m22())

        self.width_spin.setValue(width_px / PX_PER_CM)
        self.height_spin.setValue(height_px / PX_PER_CM)

    def _apply(self):
        item = self.current_item
        if item is None:
            return

        rect = item.path().boundingRect()
        if rect.width() <= 0 or rect.height() <= 0:
            return

        target_w_px = self.width_spin.value() * PX_PER_CM
        target_h_px = self.height_spin.value() * PX_PER_CM

        old_transform = item.transform()
        # Сохраняем направление отражения (Flip), если оно было применено раньше
        sign_x = -1 if old_transform.m11() < 0 else 1
        sign_y = -1 if old_transform.m22() < 0 else 1

        sx = sign_x * target_w_px / rect.width()
        sy = sign_y * target_h_px / rect.height()

        cx, cy = rect.center().x(), rect.center().y()
        new_transform = QTransform()
        new_transform.translate(cx, cy)
        new_transform.scale(sx, sy)
        new_transform.translate(-cx, -cy)

        if new_transform != old_transform:
            from .commands import TransformCommand
            self.canvas.undo_stack.push(
                TransformCommand(item, old_transform, new_transform, "Set pattern size")
            )
