from PyQt6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QDockWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .canvas import Canvas
from .tool_manager import ToolManager
from .tools.bezier_tool import BezierTool
from .pattern_panel import PatternPanel

class MainWindow(QMainWindow):
    def __init__(self, project_data):
        super().__init__()
        self.project_data = project_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Clothing Designer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем холст
        canvas_width = self.project_data.get("width", 800)
        canvas_height = self.project_data.get("height", 600)
        self.canvas = Canvas(canvas_width, canvas_height)
        self.setCentralWidget(self.canvas)
        
        # Создаем менеджер инструментов
        self.tool_manager = ToolManager(self.canvas)
        
        # Создаем интерфейс
        self.create_menu()
        self.create_toolbar()
        self.create_dock_widgets()
        self.create_statusbar()
        
        # Если открываем существующий проект, загружаем его
        if self.project_data["type"] == "existing":
            self.load_project(self.project_data["file_path"])
    
    def create_menu(self):
        menubar = self.menuBar()
        print("Menubar created")
        
        # Меню File
        file_menu = menubar.addMenu("File")
        print("File menu created")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню View (новое)
        view_menu = menubar.addMenu("View")
        print("View menu created")
        
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

        # Док-виджет для свойств инструмента Безье
        self.bezier_properties_dock = QDockWidget("Bezier Properties", self)
        self.bezier_properties_widget = QWidget()
        self.bezier_properties_layout = QVBoxLayout()
        self.bezier_properties_widget.setLayout(self.bezier_properties_layout)
        self.bezier_properties_dock.setWidget(self.bezier_properties_widget)
        self.bezier_properties_dock.setVisible(False)  # Скрываем по умолчанию
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.bezier_properties_dock)

        # Док-виджет для свойств линии
        self.line_properties_dock = QDockWidget("Line Properties", self)
        self.line_properties_widget = QWidget()
        self.line_properties_layout = QVBoxLayout()
        self.line_properties_widget.setLayout(self.line_properties_layout)
        self.line_properties_dock.setWidget(self.line_properties_widget)
        self.line_properties_dock.setVisible(False)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.line_properties_dock)
        
        # Док-виджет для шаблонов выкроек (НОВЫЙ)
        self.pattern_dock = QDockWidget("Pattern Templates", self)
        self.pattern_panel = PatternPanel()
        self.pattern_panel.pattern_selected.connect(self.on_pattern_selected)
        self.pattern_dock.setWidget(self.pattern_panel)
        self.pattern_dock.setVisible(False)  # Скрываем по умолчанию
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pattern_dock)
    
    def create_statusbar(self):
        self.statusBar().showMessage("Ready")
    
    def toggle_grid(self, checked):
        """Переключает видимость сетки на холсте"""
        self.canvas.set_grid_visibility(checked)
        status = "enabled" if checked else "disabled"
        self.statusBar().showMessage(f"Grid {status}")
    
    def load_project(self, file_path):
        # Здесь будет логика загрузки проекта
        self.statusBar().showMessage(f"Loaded project: {file_path}")







    def on_tool_changed(self, tool):
        # Показываем/скрываем панель свойств Безье
        is_bezier = isinstance(tool, BezierTool)
        self.bezier_properties_dock.setVisible(is_bezier)
        
        if is_bezier:
            self.update_bezier_properties(tool)
            
    def update_bezier_properties(self, bezier_tool):
        # Очищаем layout
        while self.bezier_properties_layout.count():
            child = self.bezier_properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Добавляем элементы управления
        from PyQt6.QtWidgets import QSlider, QLabel, QComboBox
        
        # Выбор режима
        mode_label = QLabel("Mode:")
        mode_combo = QComboBox()
        mode_combo.addItems(["Create", "Edit", "Move"])
        mode_combo.setCurrentText(bezier_tool.mode.capitalize())
        mode_combo.currentTextChanged.connect(
            lambda text: bezier_tool.set_mode(text.lower())
        )
        
        # Настройка толщины
        width_label = QLabel("Width:")
        width_slider = QSlider(Qt.Orientation.Horizontal)
        width_slider.setRange(1, 20)
        width_slider.setValue(bezier_tool.pen_width)
        width_slider.valueChanged.connect(bezier_tool.set_pen_width)
        
        self.bezier_properties_layout.addWidget(mode_label)
        self.bezier_properties_layout.addWidget(mode_combo)
        self.bezier_properties_layout.addWidget(width_label)
        self.bezier_properties_layout.addWidget(width_slider)

    def on_tool_changed(self, tool):
        # Показываем/скрываем панели свойств
        tool_name = tool.__class__.__name__
        is_bezier = tool_name == "BezierTool"
        is_line = tool_name == "LineTool"
        is_pattern = tool_name == "PatternTool"
        
        self.bezier_properties_dock.setVisible(is_bezier)
        self.line_properties_dock.setVisible(is_line)
        self.pattern_dock.setVisible(is_pattern)
        
        if is_bezier:
            self.update_bezier_properties(tool)
        elif is_line:
            self.update_line_properties(tool)
    
    def on_pattern_selected(self, template, params):
        """Обработчик выбора шаблона из панели"""
        pattern_tool = self.tool_manager.get_pattern_tool()
        if pattern_tool:
            pattern_tool.set_pattern(template, params)
            self.statusBar().showMessage(f"Pattern selected: {template.name}. Click on canvas to place it.")
            # Автоматически переключаемся на инструмент Pattern
            self.tool_manager.set_tool(pattern_tool)


    def update_line_properties(self, line_tool):
        while self.line_properties_layout.count():
            child = self.line_properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        from PyQt6.QtWidgets import QSlider, QLabel, QComboBox, QPushButton, QCheckBox
        
        # Выбор режима
        mode_label = QLabel("Mode:")
        mode_combo = QComboBox()
        mode_combo.addItems(["create", "curve", "move"])
        mode_combo.setCurrentText(line_tool.mode)
        mode_combo.currentTextChanged.connect(line_tool.set_mode)
        
        # Настройка толщины
        width_label = QLabel("Width:")
        width_slider = QSlider(Qt.Orientation.Horizontal)
        width_slider.setRange(1, 20)
        width_slider.setValue(line_tool.pen_width)
        width_slider.valueChanged.connect(line_tool.set_pen_width)
        
        # Привязка к сетке
        snap_checkbox = QCheckBox("Snap to Grid")
        snap_checkbox.setChecked(line_tool.snap_to_grid)
        snap_checkbox.stateChanged.connect(line_tool.toggle_snap_to_grid)
        
        # Кнопка сброса
        reset_button = QPushButton("Reset Line")
        reset_button.clicked.connect(lambda: line_tool.reset(self.canvas))
        
        self.line_properties_layout.addWidget(mode_label)
        self.line_properties_layout.addWidget(mode_combo)
        self.line_properties_layout.addWidget(width_label)
        self.line_properties_layout.addWidget(width_slider)
        self.line_properties_layout.addWidget(snap_checkbox)
        self.line_properties_layout.addWidget(reset_button)
        self.line_properties_layout.addStretch()

        delete_button = QPushButton("Delete Selected Line")
        delete_button.clicked.connect(lambda: self.delete_selected_line(line_tool))
        
        # Кнопка удаления всех линий
        clear_all_button = QPushButton("Clear All Lines")
        clear_all_button.clicked.connect(lambda: line_tool.reset(self.canvas))
        
        self.line_properties_layout.addWidget(mode_label)
        self.line_properties_layout.addWidget(mode_combo)
        self.line_properties_layout.addWidget(width_label)
        self.line_properties_layout.addWidget(width_slider)
        self.line_properties_layout.addWidget(snap_checkbox)
        self.line_properties_layout.addWidget(delete_button)
        self.line_properties_layout.addWidget(clear_all_button)
        self.line_properties_layout.addWidget(reset_button)
        self.line_properties_layout.addStretch()

    def delete_selected_line(self, line_tool):
        """Удаляет выбранную линию"""
        if hasattr(line_tool, 'selected_line_index') and line_tool.selected_line_index != -1:
            # Удаляем графический элемент
            line_data = line_tool.lines[line_tool.selected_line_index]
            try:
                self.canvas.scene.removeItem(line_data['path_item'])
            except:
                pass
            
            # Удаляем из списка
            line_tool.lines.pop(line_tool.selected_line_index)
            line_tool.selected_line_index = -1
            line_tool.edit_points = []
            self.canvas.viewport().update()