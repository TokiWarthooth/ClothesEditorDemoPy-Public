import sys
from PyQt6.QtWidgets import QApplication
from app.ui.startup_dialog import StartupDialog

def main():
    app = QApplication(sys.argv)

    startup_dialog = StartupDialog()
    if startup_dialog.exec() == StartupDialog.DialogCode.Accepted:
        from app.ui.main_window import MainWindow
        window = MainWindow(startup_dialog.project_data)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()