from PyQt6.QtWidgets import QMainWindow, QApplication
import sys
from view.login_window import Ui_LoginUi

class LoginController(QMainWindow, Ui_LoginUi):
    def __init__(self, model=None):
        super().__init__()
        self.model = model
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.login_to_register_btn.clicked.connect(self.login_to_register)
        self.register_to_login_btn.clicked.connect(self.register_to_login)
        self.LoginBtn.clicked.connect(self.login)
        self.LoginBtn.clicked.connect(self.perform_register)


    def login_to_register(self):
        self.stackedWidget.setCurrentIndex(1)

    def register_to_login(self):
        self.stackedWidget.setCurrentIndex(0)

    def login(self):
        login = self.LoginEdit.text()
        password = self.PasswordEdit.text()
        pass

    def perform_register(self):
        login = self.RegistLoginEdit.text()
        password = self.RegistPasswordEdit.text()
        confirm = self.RegistPasswordConfirmEdit.text()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginController()
    window.show()
    sys.exit(app.exec())