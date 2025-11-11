from PyQt6.QtWidgets import QApplication
import sys
from controller import StartUpController
import controller


def main():
    app = QApplication(sys.argv)
    controller = StartUpController()
    controller.show_login_window()
    sys.exit(app.exec())
    startup.model.close()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()