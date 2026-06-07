from PyQt6.QtGui import QUndoCommand


class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item, description="Add item"):
        super().__init__(description)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)


class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene, items, description="Delete"):
        super().__init__(description)
        self.scene = scene
        self.items = list(items)

    def redo(self):
        for item in self.items:
            self.scene.removeItem(item)

    def undo(self):
        for item in self.items:
            self.scene.addItem(item)


class ChangePenCommand(QUndoCommand):
    def __init__(self, item, old_pen, new_pen, description="Change style"):
        super().__init__(description)
        self.item = item
        self.old_pen = old_pen
        self.new_pen = new_pen

    def redo(self):
        self.item.setPen(self.new_pen)

    def undo(self):
        self.item.setPen(self.old_pen)


class TransformCommand(QUndoCommand):
    def __init__(self, item, old_transform, new_transform, description="Transform"):
        super().__init__(description)
        self.item = item
        self.old = old_transform
        self.new = new_transform

    def redo(self):
        self.item.setTransform(self.new)

    def undo(self):
        self.item.setTransform(self.old)
