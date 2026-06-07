# app/tools/text_tool.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtWidgets import QGraphicsTextItem
from .base_tool import Tool


class AnnotationTextItem(QGraphicsTextItem):
    """Текстовая метка: редактируется по двойному клику, иначе — обычный
    перетаскиваемый объект (иначе TextEditorInteraction перехватывает мышь
    у Select-инструмента, и перетаскивание не работает)."""

    def __init__(self, text=""):
        super().__init__(text)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            self.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)


class TextTool(Tool):
    """Размещает текстовую метку (QGraphicsTextItem) кликом по холсту."""

    def __init__(self):
        self.font_size = 12
        self.color = QColor(20, 20, 20)

    def mouse_press(self, event, canvas):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = canvas.mapToScene(event.pos())
            self.create_text_item(pos, canvas)

    def create_text_item(self, pos, canvas):
        item = AnnotationTextItem("Label")
        item.setDefaultTextColor(self.color)
        font = QFont()
        font.setPointSize(self.font_size)
        item.setFont(font)
        item.setPos(pos)
        item.setFlags(
            item.GraphicsItemFlag.ItemIsSelectable |
            item.GraphicsItemFlag.ItemIsMovable |
            item.GraphicsItemFlag.ItemIsFocusable
        )
        item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        from ..commands import AddItemCommand
        canvas.undo_stack.push(AddItemCommand(canvas.scene, item, "Add text label"))

        item.setFocus()
        cursor = item.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        item.setTextCursor(cursor)

    def set_font_size(self, size):
        self.font_size = size

    def set_color(self, color):
        self.color = color

    def get_cursor(self):
        return Qt.CursorShape.IBeamCursor
