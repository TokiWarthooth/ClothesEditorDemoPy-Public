import sys
from PyQt6.QtWidgets import QApplication
from app.startup_dialog import StartupDialog

def main():
    app = QApplication(sys.argv)
    
    # Показываем стартовое окно
    startup_dialog = StartupDialog()
    if startup_dialog.exec() == StartupDialog.DialogCode.Accepted:
        # Если пользователь выбрал действие, запускаем главное окно
        from app.main_window import MainWindow
        window = MainWindow(startup_dialog.project_data)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()