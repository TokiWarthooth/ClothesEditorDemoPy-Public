from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame, QGraphicsTextItem
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QUndoStack
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

class Canvas(QGraphicsView):
    mouse_moved = pyqtSignal(QPointF)

    def __init__(self, width, height):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, width, height)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Настройки по умолчанию
        self.current_tool = None
        self.pen_color = QColor("black")
        self.pen_width = 2
        self.fill_color = QColor(0, 0, 0, 0)  # Прозрачная заливка
        
        # Настройки темы и сетки
        self.theme = "light"  # По умолчанию светлая тема
        self.show_grid = True  # Показывать сетку по умолчанию
        self.grid_size = 20  # Размер клетки сетки в пикселях
        self.grid_color_light = QColor(220, 220, 220)  # Цвет сетки для светлой темы
        self.grid_color_dark = QColor(80, 80, 80)  # Цвет сетки для темной темы
        
        self.undo_stack = QUndoStack(self)

        # Установим начальную тему
        self.set_theme(self.theme)
        
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
        
    def drawBackground(self, painter, rect):
        """Переопределяем метод отрисовки фона для добавления сетки"""
        # Сначала рисуем стандартный фон
        super().drawBackground(painter, rect)
        
        # Если сетка включена, рисуем её
        if self.show_grid:
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))
            
            # Получаем границы сцены
            scene_rect = self.sceneRect()
            left = int(scene_rect.left())
            right = int(scene_rect.right())
            top = int(scene_rect.top())
            bottom = int(scene_rect.bottom())
            
            # Рисуем вертикальные линии
            for x in range(left, right + 1, self.grid_size):
                painter.drawLine(x, top, x, bottom)
                
            # Рисуем горизонтальные линии
            for y in range(top, bottom + 1, self.grid_size):
                painter.drawLine(left, y, right, y)
                
            # Рисуем более заметные линии каждые 5 клеток
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.SolidLine))
            for x in range(left, right + 1, self.grid_size * 5):
                painter.drawLine(x, top, x, bottom)
            for y in range(top, bottom + 1, self.grid_size * 5):
                painter.drawLine(left, y, right, y)
    
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
                from .commands import RemoveItemsCommand
                self.undo_stack.push(RemoveItemsCommand(self.scene, items))
        else:
            super().keyPressEvent(event)

    def get_current_pen(self):
        """Возвращает QPen с текущими настройками"""
        pen = QPen(self.pen_color, self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen
    

