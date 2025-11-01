from .main_window_controllers import MainWindowController
from .login_controller import LoginController
from model import Model
from PyQt6.QtWidgets import QMessageBox


class StartUpController:
    def __init__(self):
        self.model = Model()
        self.login_window = LoginController(model=self.model.get_auth())
        self.main_window = None
        self.login_window.login_successful.connect(self.close_login_window_and_open_main_window)

    def show_login_window(self):
        self.login_window.show()

    def close_login_window_and_open_main_window(self, user_ud):
        try:
            self.login_window.hide()
            self.main_window = MainWindowController(user_id=user_ud, model=self.model.get_user())
            self.main_window.show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть главное окно:\n{e}")
