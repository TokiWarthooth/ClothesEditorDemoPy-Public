from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtCore import Qt

class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.project_data = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Clothing Designer - Start")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        title = QLabel("Clothing Designer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        btn_new = QPushButton("New Project")
        btn_open = QPushButton("Open Project")
        btn_exit = QPushButton("Exit")
        
        btn_new.clicked.connect(self.create_new_project)
        btn_open.clicked.connect(self.open_project)
        btn_exit.clicked.connect(self.reject)
        
        layout.addWidget(title)
        layout.addWidget(btn_new)
        layout.addWidget(btn_open)
        layout.addWidget(btn_exit)
        
        self.setLayout(layout)
    
    def create_new_project(self):
        # Здесь можно добавить диалог для настройки нового проекта
        self.project_data = {
            "type": "new",
            "width": 800,
            "height": 600,
            "background": "#FFFFFF"
        }
        self.accept()
    
    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Clothing Designer Files (*.cld)"
        )
        if file_path:
            # Здесь будет логика загрузки проекта
            self.project_data = {
                "type": "existing",
                "file_path": file_path
            }
            self.accept()