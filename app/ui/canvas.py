import math
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame, QGraphicsTextItem
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QUndoStack
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

class Canvas(QGraphicsView):
    mouse_moved = pyqtSignal(QPointF)
    zoom_changed = pyqtSignal(float)

    MIN_ZOOM = 0.1
    MAX_ZOOM = 8.0
    ZOOM_STEP = 1.15

    def __init__(self, width, height):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, width, height)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Зум колёсиком мыши всегда центрируется под курсором
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.zoom_level = 1.0

        # Настройки по умолчанию
        self.current_tool = None
        self.pen_color = QColor("black")
        self.pen_width = 2
        self.fill_color = QColor(0, 0, 0, 0)  # Прозрачная заливка

        # Настройки темы и сетки
        self.theme = "light"  # По умолчанию светлая тема
        self.show_grid = True  # Показывать сетку по умолчанию
        self.grid_size = 20  # Размер клетки сетки в пикселях (базовый, при 100% зуме)
        self.grid_color_light = QColor(220, 220, 220)  # Цвет сетки для светлой темы
        self.grid_color_dark = QColor(80, 80, 80)  # Цвет сетки для темной темы

        self.undo_stack = QUndoStack(self)

        # Установим начальную тему
        self.set_theme(self.theme)

    def wheelEvent(self, event):
        """Зум колёсиком мыши, с центром под курсором."""
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return

        factor = self.ZOOM_STEP if delta > 0 else 1 / self.ZOOM_STEP
        new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom_level * factor))
        applied_factor = new_zoom / self.zoom_level
        if applied_factor != 1.0:
            self.scale(applied_factor, applied_factor)
            self.zoom_level = new_zoom
            self.zoom_changed.emit(self.zoom_level)
            self.viewport().update()
        event.accept()
        
    def set_theme(self, theme_name):
        """Устанавливает тему оформления холста"""
        self.theme = theme_name
        
        if theme_name == "light":
            self.setBackgroundBrush(QColor(240, 240, 240))  # Светлый фон
            self.grid_color = self.grid_color_light
            # Для светлой темы - темные цвета инструментов
            self.pen_color = QColor("black")
        elif theme_name == "dark":
            self.setBackgroundBrush(QColor(50, 50, 50))  # Темный фон
            self.grid_color = self.grid_color_dark
            # Для темной темы - светлые цвета инструментов
            self.pen_color = QColor("white")
        
        # Обновляем отображение
        self.viewport().update()
        
    def set_grid_visibility(self, visible):
        """Включает или выключает отображение сетки"""
        self.show_grid = visible
        self.viewport().update()
        
    def set_grid_size(self, size):
        """Устанавливает размер клетки сетки"""
        self.grid_size = size
        self.viewport().update()

    def set_scene_size(self, width, height):
        """Изменяет размер рабочей плоскости (холста)."""
        self.scene.setSceneRect(0, 0, width, height)
        self.viewport().update()
        
    def _effective_grid_step(self):
        """Подбирает шаг сетки в координатах сцены так, чтобы на экране
        клетка оставалась примерно одного размера — при увеличении масштаба
        сетка мельчает (шаг делится пополам), при уменьшении — укрупняется."""
        scale = self.transform().m11()
        if scale <= 0:
            return self.grid_size

        min_px, max_px = 15.0, 60.0
        step = float(self.grid_size)
        px = step * scale

        guard = 0
        while px > max_px and guard < 12:
            step /= 2
            px /= 2
            guard += 1
        while px < min_px and guard < 24:
            step *= 2
            px *= 2
            guard += 1

        return step

    def drawBackground(self, painter, rect):
        """Переопределяем метод отрисовки фона для добавления сетки"""
        # Сначала рисуем стандартный фон
        super().drawBackground(painter, rect)

        # Если сетка включена, рисуем её
        if self.show_grid:
            step = self._effective_grid_step()
            if step <= 0:
                return

            # Пересекаем видимую область со сценой, чтобы не рисовать лишнее
            scene_rect = self.sceneRect().intersected(rect)
            left = scene_rect.left()
            right = scene_rect.right()
            top = scene_rect.top()
            bottom = scene_rect.bottom()
            if right <= left or bottom <= top:
                return

            # Мелкие (второстепенные) линии — ширина 0 = "косметическое" перо,
            # всегда ровно 1 пиксель на экране независимо от масштаба
            pen_minor = QPen(self.grid_color, 0, Qt.PenStyle.DotLine)
            painter.setPen(pen_minor)

            x = math.floor(left / step) * step
            while x <= right:
                painter.drawLine(QPointF(x, top), QPointF(x, bottom))
                x += step

            y = math.floor(top / step) * step
            while y <= bottom:
                painter.drawLine(QPointF(left, y), QPointF(right, y))
                y += step

            # Более заметные (главные) линии каждые 5 мелких клеток
            major_step = step * 5
            pen_major = QPen(self.grid_color, 0, Qt.PenStyle.SolidLine)
            painter.setPen(pen_major)

            x = math.floor(left / major_step) * major_step
            while x <= right:
                painter.drawLine(QPointF(x, top), QPointF(x, bottom))
                x += major_step

            y = math.floor(top / major_step) * major_step
            while y <= bottom:
                painter.drawLine(QPointF(left, y), QPointF(right, y))
                y += major_step
    
    def set_tool(self, tool):
        self.current_tool = tool
        if getattr(tool, 'use_scene_events', False):
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def _use_scene(self):
        return getattr(self.current_tool, 'use_scene_events', False)

    def mousePressEvent(self, event):
        if self.current_tool and not self._use_scene():
            self.current_tool.mouse_press(event, self)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_moved.emit(self.mapToScene(event.pos()))
        if self.current_tool and not self._use_scene():
            self.current_tool.mouse_move(event, self)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.current_tool and not self._use_scene():
            self.current_tool.mouse_release(event, self)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        focus_item = self.scene.focusItem()
        if (isinstance(focus_item, QGraphicsTextItem)
                and focus_item.textInteractionFlags() != Qt.TextInteractionFlag.NoTextInteraction):
            # Текст редактируется — отдаём клавишу редактору, а не удалению объектов
            super().keyPressEvent(event)
            return

        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            items = self.scene.selectedItems()
            if items:
                from ..core.commands import RemoveItemsCommand
                self.undo_stack.push(RemoveItemsCommand(self.scene, items))
        else:
            super().keyPressEvent(event)

    def get_current_pen(self):
        """Возвращает QPen с текущими настройками"""
        pen = QPen(self.pen_color, self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen
    

