from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from PyQt6.QtCore import pyqtSignal
from view.login_window import Ui_LoginUi


class LoginController(QMainWindow, Ui_LoginUi):
    login_successful = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.login_to_register_btn.clicked.connect(self.login_to_register)
        self.register_to_login_btn.clicked.connect(self.register_to_login)
        self.LoginBtn.clicked.connect(self.login)
        self.RegisterBtnNewUser.clicked.connect(self.perform_register)
        self.RegistShowPwd.clicked.connect(self.toggle_pwd_on_register_tab)
        self.LoginShowPwd.clicked.connect(self.toggle_pwd_on_login_tab)

    def login_to_register(self):
        self.stackedWidget.setCurrentIndex(1)

    def register_to_login(self):
        self.stackedWidget.setCurrentIndex(0)

    def login(self):
        login = self.LoginEdit.text().strip()
        password = self.PasswordEdit.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        user = self.model.login_user(login, password)
        if user is True:
            user_id = self.model.get_user_id(login)  # получаем ID пользователя из базы
            self.login_successful.emit(user_id)

            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def perform_register(self):
        login = self.RegistLoginEdit.text().strip()
        password = self.RegistPasswordEdit.text().strip()
        confirm = self.RegistPasswordConfirmEdit.text().strip()
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        elif not login or not password or not confirm:
            QMessageBox.warning(self, "Ошибка", "Введите логин, пароль и подтвердите его!")
            return

        elif len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Ваш пароль слишком короткий")
            return

        success = self.model.register_user(login, password)

        if success:

            QMessageBox.information(self, "Успешно", "Аккаунт создан! Теперь войдите в систему.")
            self.register_to_login()

        else:

            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует.")

    def toggle_pwd_on_register_tab(self):
        current_mode = self.RegistPasswordEdit.echoMode()

        if current_mode == QLineEdit.EchoMode.Password:
            # показать пароль
            self.RegistPasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.RegistPasswordConfirmEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.RegistShowPwd.setText("🙈")
        else:
            # скрыть пароль
            self.RegistPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.RegistPasswordConfirmEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.RegistShowPwd.setText("👁")

    def toggle_pwd_on_login_tab(self):
        current_mode = self.PasswordEdit.echoMode()

        if current_mode == QLineEdit.EchoMode.Password:
            self.PasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.LoginShowPwd.setText("🙈")
        else:
            self.PasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.LoginShowPwd.setText("👁")
