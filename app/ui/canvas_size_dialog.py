# app/ui/canvas_size_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QDialogButtonBox


class CanvasSizeDialog(QDialog):
    """Диалог изменения размера рабочей плоскости (холста)."""

    def __init__(self, measurements, current_width_px, current_height_px, parent=None):
        super().__init__(parent)
        self.measurements = measurements
        self.setWindowTitle("Canvas Size")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        unit = measurements.unit
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 1_000_000)
        self.width_spin.setDecimals(1)
        self.width_spin.setSuffix(f" {unit}")
        self.width_spin.setValue(measurements.px_to_unit(current_width_px))

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 1_000_000)
        self.height_spin.setDecimals(1)
        self.height_spin.setSuffix(f" {unit}")
        self.height_spin.setValue(measurements.px_to_unit(current_height_px))

        form.addRow("Width:", self.width_spin)
        form.addRow("Height:", self.height_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_size_px(self):
        return (
            self.measurements.unit_to_px(self.width_spin.value()),
            self.measurements.unit_to_px(self.height_spin.value()),
        )
