from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QPushButton, QFrame, QGraphicsTextItem)
from PyQt6.QtGui import QFont, QColor

_NUMBER_TAG = "part_number"
_NUMBER_KEY = 2


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #ccc;")
    return line


class AnnotationsPanel(QWidget):
    """Текстовые метки, стрелки долевой нити, нумерация деталей."""

    def __init__(self, canvas, tool_manager, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.tool_manager = tool_manager
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Annotations")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        # --- Текстовые метки ---
        layout.addWidget(QLabel("Text label:"))
        row = QHBoxLayout()
        row.addWidget(QLabel("Font size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        row.addWidget(self.font_size_spin)
        layout.addLayout(row)

        btn_text = QPushButton("Add Text Label")
        btn_text.setToolTip("Кликните на холсте, чтобы поставить метку")
        btn_text.clicked.connect(self._activate_text_tool)
        layout.addWidget(btn_text)

        layout.addWidget(_separator())

        # --- Долевая нить ---
        layout.addWidget(QLabel("Grainline arrow:"))
        btn_arrow = QPushButton("Add Grainline Arrow")
        btn_arrow.setToolTip("Кликните дважды: начало и конец стрелки")
        btn_arrow.clicked.connect(self._activate_grainline_tool)
        layout.addWidget(btn_arrow)

        layout.addWidget(_separator())

        # --- Нумерация деталей ---
        layout.addWidget(QLabel("Part numbering:"))
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Start at:"))
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setRange(1, 999)
        self.start_number_spin.setValue(1)
        row2.addWidget(self.start_number_spin)
        layout.addLayout(row2)

        btn_number = QPushButton("Number Selected Parts")
        btn_number.setToolTip("Выберите детали (Select), затем нажмите")
        btn_number.clicked.connect(self._number_selected)
        layout.addWidget(btn_number)

        btn_remove_numbers = QPushButton("Remove Number Labels")
        btn_remove_numbers.clicked.connect(self._remove_numbers)
        layout.addWidget(btn_remove_numbers)

        hint = QLabel("Tip: select pattern pieces with the\n"
                      "Select tool before numbering them.")
        hint.setStyleSheet("color: #888; font-size: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

    # --- Текстовые метки ---
    def _on_font_size_changed(self, value):
        tool = self.tool_manager.get_text_tool()
        if tool:
            tool.set_font_size(value)

    def _activate_text_tool(self):
        tool = self.tool_manager.get_text_tool()
        if tool:
            tool.set_font_size(self.font_size_spin.value())
            self.tool_manager.set_tool(tool)
            self.canvas.window().statusBar().showMessage(
                "Click on the canvas to place a text label"
            )

    # --- Долевая нить ---
    def _activate_grainline_tool(self):
        tool = self.tool_manager.get_grainline_tool()
        if tool:
            self.tool_manager.set_tool(tool)
            self.canvas.window().statusBar().showMessage(
                "Click for arrow start, click again for arrow end"
            )

    # --- Нумерация деталей ---
    def _number_selected(self):
        from .commands import AddItemCommand

        items = [i for i in self.canvas.scene.selectedItems()
                 if i.data(_NUMBER_KEY) != _NUMBER_TAG]
        if not items:
            return

        number = self.start_number_spin.value()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        for item in items:
            label = QGraphicsTextItem(str(number))
            label.setDefaultTextColor(QColor(20, 20, 20))
            label.setFont(font)

            center = item.sceneBoundingRect().center()
            br = label.boundingRect()
            label.setPos(center.x() - br.width() / 2, center.y() - br.height() / 2)
            label.setData(_NUMBER_KEY, _NUMBER_TAG)
            label.setFlags(
                label.GraphicsItemFlag.ItemIsSelectable |
                label.GraphicsItemFlag.ItemIsMovable
            )

            self.canvas.undo_stack.push(
                AddItemCommand(self.canvas.scene, label, f"Number part #{number}")
            )
            number += 1

        self.start_number_spin.setValue(number)

    def _remove_numbers(self):
        from .commands import RemoveItemsCommand
        labels = [i for i in self.canvas.scene.items()
                  if i.data(_NUMBER_KEY) == _NUMBER_TAG]
        if labels:
            self.canvas.undo_stack.push(
                RemoveItemsCommand(self.canvas.scene, labels, "Remove part numbers")
            )
