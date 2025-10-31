from PyQt6.QtWidgets import QApplication
import sys
from PyQt6.QtWidgets import QMessageBox
from controller import MainWindowController


def main():
    app = QApplication(sys.argv)
    main_app = MainWindowController()


    main_app.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()