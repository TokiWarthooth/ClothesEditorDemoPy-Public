from PyQt6.QtWidgets import (QMainWindow, QToolBar, QDockWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QFileDialog, QMessageBox, QLabel, QComboBox)
from PyQt6.QtGui import QAction, QTransform
from PyQt6.QtCore import Qt
from .canvas import Canvas
from .tool_manager import ToolManager
from .pattern_panel import PatternPanel
from .project_manager import ProjectManager
from .measurements import MeasurementSystem
from .rulers import HorizontalRuler, VerticalRuler, RULER_SIZE
from .seam_panel import SeamAllowancePanel
from .seam_style_panel import SeamStylePanel
from .annotations_panel import AnnotationsPanel
from .pattern_size_panel import PatternSizePanel

class MainWindow(QMainWindow):
    def __init__(self, project_data):
        super().__init__()
        self.project_data = project_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Clothing Designer")
        self.setGeometry(100, 100, 1200, 800)

        # Система измерений
        self.measurements = MeasurementSystem("cm")

        # Холст
        canvas_width  = self.project_data.get("width", 800)
        canvas_height = self.project_data.get("height", 600)
        self.canvas = Canvas(canvas_width, canvas_height)

        # Линейки
        self.h_ruler = HorizontalRuler(self.canvas, self.measurements)
        self.v_ruler = VerticalRuler(self.canvas, self.measurements)

        # Центральный виджет: угол + линейки + холст
        central = QWidget()
        grid = QGridLayout(central)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        corner = QWidget()
        corner.setFixedSize(RULER_SIZE, RULER_SIZE)
        corner.setStyleSheet("background-color: #d0d0d0;")

        grid.addWidget(corner,        0, 0)
        grid.addWidget(self.h_ruler,  0, 1)
        grid.addWidget(self.v_ruler,  1, 0)
        grid.addWidget(self.canvas,   1, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)

        self.setCentralWidget(central)

        # Менеджеры
        self.tool_manager = ToolManager(self.canvas)
        self.project_manager = ProjectManager()
        self.current_file_path = None

        # UI
        self.create_menu()
        self.create_toolbar()
        self.create_dock_widgets()
        self.create_statusbar()

        # Сигналы
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        self.canvas.horizontalScrollBar().valueChanged.connect(self.h_ruler.update)
        self.canvas.verticalScrollBar().valueChanged.connect(self.v_ruler.update)

        if self.project_data["type"] == "existing":
            self.load_project(self.project_data["file_path"])
    
    def create_menu(self):
        menubar = self.menuBar()

        # Меню File
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project_dialog)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Edit
        edit_menu = menubar.addMenu("Edit")

        # Undo/Redo — создаём через QUndoStack, чтобы автоматически менялся текст и enabled
        undo_action = self.canvas.undo_stack.createUndoAction(self, "Undo")
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = self.canvas.undo_stack.createRedoAction(self, "Redo")
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        flip_h = QAction("Flip Horizontal", self)
        flip_h.setShortcut("Shift+H")
        flip_h.triggered.connect(lambda: self._flip_items(horizontal=True))
        edit_menu.addAction(flip_h)

        flip_v = QAction("Flip Vertical", self)
        flip_v.setShortcut("Shift+V")
        flip_v.triggered.connect(lambda: self._flip_items(horizontal=False))
        edit_menu.addAction(flip_v)

        # Меню View
        view_menu = menubar.addMenu("View")
        
        # Подменю Themes
        themes_menu = view_menu.addMenu("Themes")
        
        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(lambda: self.canvas.set_theme("light"))
        themes_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(lambda: self.canvas.set_theme("dark"))
        themes_menu.addAction(dark_theme_action)
        
        # Переключение сетки
        self.grid_action = QAction("Show Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.toggle_grid)
        view_menu.addAction(self.grid_action)
        
        # Настройки сетки
        grid_menu = view_menu.addMenu("Grid Size")
        
        small_grid = QAction("Small (10px)", self)
        small_grid.triggered.connect(lambda: self.canvas.set_grid_size(10))
        grid_menu.addAction(small_grid)
        
        medium_grid = QAction("Medium (20px)", self)
        medium_grid.triggered.connect(lambda: self.canvas.set_grid_size(20))
        grid_menu.addAction(medium_grid)
        
        large_grid = QAction("Large (30px)", self)
        large_grid.triggered.connect(lambda: self.canvas.set_grid_size(30))
        grid_menu.addAction(large_grid)
        
        # Меню Tools (новое)
        tools_menu = menubar.addMenu("Tools")
        # Здесь можно добавить дополнительные инструменты
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Добавляем инструменты через менеджер инструментов
        for tool_name, tool_action in self.tool_manager.get_tool_actions().items():
            toolbar.addAction(tool_action)
    
    def create_dock_widgets(self):
        # Док-виджет для палитры цветов
        color_dock = QDockWidget("Colors", self)
        color_widget = QWidget()
        color_layout = QVBoxLayout()
        color_widget.setLayout(color_layout)
        color_dock.setWidget(color_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, color_dock)
        
        # Док-виджет для слоев
        layers_dock = QDockWidget("Layers", self)
        layers_widget = QWidget()
        layers_layout = QVBoxLayout()
        layers_widget.setLayout(layers_layout)
        layers_dock.setWidget(layers_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)
        
        # Док-виджет для свойств инструментов (новый)
        properties_dock = QDockWidget("Properties", self)
        properties_widget = QWidget()
        properties_layout = QVBoxLayout()
        properties_widget.setLayout(properties_layout)
        properties_dock.setWidget(properties_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, properties_dock)

        # Dok — шаблоны выкроек
        self.pattern_dock = QDockWidget("Pattern Templates", self)
        self.pattern_panel = PatternPanel()
        self.pattern_panel.pattern_selected.connect(self.on_pattern_selected)
        self.pattern_dock.setWidget(self.pattern_panel)
        self.pattern_dock.setVisible(False)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pattern_dock)

        # Dok — точный размер выбранной детали выкройки
        self.pattern_size_dock = QDockWidget("Pattern Size", self)
        self.pattern_size_dock.setWidget(PatternSizePanel(self.canvas))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.pattern_size_dock)

        # Dok — припуски на швы
        self.seam_dock = QDockWidget("Seam Allowance", self)
        self.seam_dock.setWidget(SeamAllowancePanel(self.canvas))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.seam_dock)

        # Dok — обозначения (стили) швов
        self.seam_style_dock = QDockWidget("Seam Style", self)
        self.seam_style_dock.setWidget(SeamStylePanel(self.canvas))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.seam_style_dock)

        # Dok — аннотации (текст, долевая нить, нумерация)
        self.annotations_dock = QDockWidget("Annotations", self)
        self.annotations_dock.setWidget(AnnotationsPanel(self.canvas, self.tool_manager))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.annotations_dock)

    def create_statusbar(self):
        sb = self.statusBar()

        # Переключатель единиц (постоянный виджет, справа)
        unit_widget = QWidget()
        unit_layout = QHBoxLayout(unit_widget)
        unit_layout.setContentsMargins(6, 0, 6, 0)
        unit_layout.setSpacing(4)
        unit_layout.addWidget(QLabel("Units:"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["cm", "mm", "px"])
        self.unit_combo.setFixedWidth(55)
        self.unit_combo.currentTextChanged.connect(self._on_unit_changed)
        unit_layout.addWidget(self.unit_combo)
        sb.addPermanentWidget(unit_widget)

        # Координаты курсора (постоянный виджет, справа)
        self.coord_label = QLabel("X: —   Y: —")
        self.coord_label.setMinimumWidth(200)
        sb.addPermanentWidget(self.coord_label)

        sb.showMessage("Ready")
    
    def _on_mouse_moved(self, scene_pos):
        self.coord_label.setText(
            self.measurements.format_coord(scene_pos.x(), scene_pos.y())
        )
        self.h_ruler.update_cursor(scene_pos.x(), scene_pos.y())
        self.v_ruler.update_cursor(scene_pos.x(), scene_pos.y())

    def _on_unit_changed(self, unit):
        self.measurements.unit = unit
        self.h_ruler.update()
        self.v_ruler.update()

    def _flip_items(self, horizontal: bool):
        from .commands import TransformCommand
        items = self.canvas.scene.selectedItems()
        if not items:
            self.statusBar().showMessage("Select items first (use Select tool)")
            return

        for item in items:
            center = item.boundingRect().center()
            cx, cy = center.x(), center.y()
            t = QTransform()
            t.translate(cx, cy)
            t.scale(-1 if horizontal else 1, 1 if horizontal else -1)
            t.translate(-cx, -cy)
            old_tf = item.transform()
            new_tf = old_tf * t
            desc = "Flip horizontal" if horizontal else "Flip vertical"
            self.canvas.undo_stack.push(TransformCommand(item, old_tf, new_tf, desc))

        axis = "horizontal" if horizontal else "vertical"
        self.statusBar().showMessage(f"Flipped {len(items)} item(s) {axis}")

    def toggle_grid(self, checked):
        """Переключает видимость сетки на холсте"""
        self.canvas.set_grid_visibility(checked)
        status = "enabled" if checked else "disabled"
        self.statusBar().showMessage(f"Grid {status}")
    
    def new_project(self):
        reply = QMessageBox.question(
            self, "New Project",
            "Create a new project? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.scene.clear()
            self.current_file_path = None
            self.setWindowTitle("Clothing Designer")
            self.statusBar().showMessage("New project created")

    def open_project_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Clothing Designer Files (*.cld)"
        )
        if file_path:
            self.load_project(file_path)

    def save_project_dialog(self):
        if self.current_file_path:
            self._do_save(self.current_file_path)
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project", "", "Clothing Designer Files (*.cld)"
            )
            if file_path:
                self._do_save(file_path)

    def _do_save(self, file_path):
        self.project_manager.current_project = {
            "width": int(self.canvas.sceneRect().width()),
            "height": int(self.canvas.sceneRect().height()),
            "background": "#FFFFFF",
            "layers": [],
            "objects": []
        }
        if self.project_manager.save_project(file_path):
            self.current_file_path = file_path
            self.setWindowTitle(f"Clothing Designer — {file_path.split('/')[-1]}")
            self.statusBar().showMessage(f"Saved: {file_path}")
        else:
            QMessageBox.warning(self, "Save Error", "Could not save the project.")

    def load_project(self, file_path):
        data = self.project_manager.load_project(file_path)
        if data:
            self.canvas.scene.clear()
            self.current_file_path = file_path
            self.setWindowTitle(f"Clothing Designer — {file_path.split('/')[-1]}")
            self.statusBar().showMessage(f"Opened: {file_path}")
        else:
            QMessageBox.warning(self, "Open Error", f"Could not open: {file_path}")







    def on_tool_changed(self, tool):
        # Показываем/скрываем панели свойств
        tool_name = tool.__class__.__name__
        is_pattern = tool_name == "PatternTool"

        self.pattern_dock.setVisible(is_pattern)

    def on_pattern_selected(self, template, params):
        """Обработчик выбора шаблона из панели"""
        pattern_tool = self.tool_manager.get_pattern_tool()
        if pattern_tool:
            pattern_tool.set_pattern(template, params)
            self.statusBar().showMessage(f"Pattern selected: {template.name}. Click on canvas to place it.")
            # Автоматически переключаемся на инструмент Pattern
            self.tool_manager.set_tool(pattern_tool)