# app/pattern_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QSlider, QScrollArea, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPen, QColor
from .pattern_templates import PatternLibrary

class PatternPanel(QWidget):
    """Панель для работы с шаблонами выкроек"""
    pattern_selected = pyqtSignal(object, dict)  # Сигнал при выборе шаблона
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.library = PatternLibrary()
        self.current_template = None
        self.current_params = {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Pattern Templates")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Выбор категории
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.library.get_categories())
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        
        layout.addWidget(category_label)
        layout.addWidget(self.category_combo)
        
        # Выбор шаблона
        template_label = QLabel("Template:")
        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        
        layout.addWidget(template_label)
        layout.addWidget(self.template_combo)
        
        # Область прокрутки для параметров
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        scroll.setWidget(self.params_widget)
        
        layout.addWidget(scroll)
        
        # Кнопка добавления на холст
        self.add_button = QPushButton("Add to Canvas")
        self.add_button.clicked.connect(self.on_add_clicked)
        self.add_button.setEnabled(False)
        layout.addWidget(self.add_button)
        
        # Кнопки управления размещенными шаблонами
        buttons_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        buttons_layout.addWidget(self.clear_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Загружаем первую категорию
        self.on_category_changed(self.category_combo.currentText())
        
    def on_category_changed(self, category):
        """Обработчик смены категории"""
        self.template_combo.clear()
        templates = self.library.get_templates_by_category(category)
        for template in templates:
            self.template_combo.addItem(template.name, template)
            
    def on_template_changed(self, index):
        """Обработчик смены шаблона"""
        if index < 0:
            return
            
        self.current_template = self.template_combo.itemData(index)
        if self.current_template:
            self.load_parameters()
            self.add_button.setEnabled(True)
        else:
            self.add_button.setEnabled(False)
            
    def load_parameters(self):
        """Загружает параметры текущего шаблона"""
        # Очищаем предыдущие параметры
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.current_params = {}
        
        if not self.current_template:
            return
            
        # Создаем элементы управления для каждого параметра
        params = self.current_template.get_parameters()
        
        for param in params:
            group = QGroupBox(param["label"])
            group_layout = QVBoxLayout()
            
            # Слайдер
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(param["min"])
            slider.setMaximum(param["max"])
            slider.setValue(param["default"])
            
            # Метка со значением
            value_label = QLabel(str(param["default"]))
            
            # Обновление значения
            def make_update_func(param_name, label):
                def update_value(value):
                    label.setText(str(value))
                    self.current_params[param_name] = value
                return update_value
                
            slider.valueChanged.connect(make_update_func(param["name"], value_label))
            
            # Инициализируем значение
            self.current_params[param["name"]] = param["default"]
            
            # Компоновка
            value_layout = QHBoxLayout()
            value_layout.addWidget(value_label)
            value_layout.addStretch()
            
            group_layout.addLayout(value_layout)
            group_layout.addWidget(slider)
            group.setLayout(group_layout)
            
            self.params_layout.addWidget(group)
            
        self.params_layout.addStretch()
        
    def on_add_clicked(self):
        """Обработчик нажатия кнопки добавления"""
        if self.current_template:
            self.pattern_selected.emit(self.current_template, self.current_params)
    
    def on_delete_clicked(self):
        """Обработчик удаления выбранного шаблона"""
        # Получаем pattern_tool из родительского окна
        main_window = self.window()
        if hasattr(main_window, 'tool_manager'):
            pattern_tool = main_window.tool_manager.get_pattern_tool()
            if pattern_tool:
                pattern_tool.delete_selected_pattern(main_window.canvas)
    
    def on_clear_clicked(self):
        """Обработчик очистки всех шаблонов"""
        main_window = self.window()
        if hasattr(main_window, 'tool_manager'):
            pattern_tool = main_window.tool_manager.get_pattern_tool()
            if pattern_tool:
                pattern_tool.clear_all_patterns(main_window.canvas)
