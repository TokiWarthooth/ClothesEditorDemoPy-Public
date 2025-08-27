import json
from PyQt6.QtGui import QImage

class ProjectManager:
    def __init__(self):
        self.current_project = None
        
    def new_project(self, width, height, background="#FFFFFF"):
        self.current_project = {
            "width": width,
            "height": height,
            "background": background,
            "layers": [],
            "objects": []
        }
        return self.current_project
        
    def save_project(self, file_path):
        if self.current_project:
            with open(file_path, 'w') as f:
                json.dump(self.current_project, f)
            return True
        return False
        
    def load_project(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.current_project = json.load(f)
            return self.current_project
        except:
            return None
            
    def export_image(self, file_path, format="PNG"):
        # Здесь будет логика экспорта изображения
        pass