from .main_window_controllers import MainWindowController
from .login_controller import LoginController
from model import Model
from PyQt6.QtWidgets import QMessageBox


class StartUpController:
    def __init__(self):
        self.model = Model()
        self.login_window = LoginController(self.model.get_auth())
        self.main_window = None
        self.login_window.login_successful.connect(self.close_login_window_and_open_main_window)

    def show_login_window(self):
        self.login_window.show()

    def close_login_window_and_open_main_window(self, user_id=1):
        try:
            self.login_window.hide()
            self.model.init_user(user_id)
            self.main_window = MainWindowController(model=self.model, user_id=user_id)
            self.main_window.show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть главное окно:\n{e}")