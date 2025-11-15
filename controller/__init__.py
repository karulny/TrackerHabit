from .main_window_controllers import MainWindowController
from .login_controller import LoginController
from model import Model
from PyQt6.QtWidgets import QMessageBox
import traceback


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
            self.main_window = MainWindowController(model=self.model)
            self.main_window.show()
            self.main_window.unlogin_from_main.connect(self.restart_login_window)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть главное окно:\n{e}")

    def restart_login_window(self):
        """Перезапускает окно логина после выхода из аккаунта"""
        try:
            # Закрываем главное окно
            if self.main_window:
                self.main_window.close()
            
            if self.model:
                # Обновляем last_login (пока БД открыта)
                self.model.close()
                
                # Закрываем соединение с БД
                if hasattr(self.model, 'database'):
                    self.model.database.close()
                
                # Обнуляем ссылку на старую модель
                self.model = None
            
            # Создаём новую модель с новым соединением к БД
            self.model = Model()
            
            # Создаём новое окно логина
            self.login_window = LoginController(self.model.get_auth())
            self.login_window.login_successful.connect(self.close_login_window_and_open_main_window)
            self.login_window.show()
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось перезапустить окно входа:\n{e}")