from .main_window_controllers import MainWindowController
from .login_controller import LoginController
from model import Model
from PyQt6.QtWidgets import QMessageBox, QApplication
import traceback


class StartUpController:
    """
    Главный контроллер приложения.
    Управляет переключением между окном входа и главным окном.
    """

    def __init__(self):
        # Создаём модель ОДИН РАЗ при запуске приложения
        self.model = Model()
        self.login_window = None
        self.main_window = None
        
        # Создаём окно входа
        self._create_login_window()

    def _create_login_window(self):
        """Создаёт или пересоздаёт окно входа"""
        self.login_window = LoginController(self.model.get_auth())
        self.login_window.login_successful.connect(self.open_main_window)

    def show_login_window(self):
        """Показывает окно входа"""
        if self.login_window:
            self.login_window.show()

    def open_main_window(self, user_id):
        """Открывает главное окно после успешного входа"""
        try:
            # Скрываем окно входа
            if self.login_window:
                self.login_window.hide()
            
            # Инициализируем пользователя в модели
            self.model.init_user(user_id)
            
            # Создаём главное окно
            self.main_window = MainWindowController(model=self.model)
            self.main_window.show()
            
            # Подключаем сигнал выхода
            self.main_window.unlogin_from_main.connect(self.logout_and_show_login)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                None, 
                "Ошибка", 
                f"Не удалось открыть главное окно:\n{e}"
            )

    def logout_and_show_login(self):
        """
        Выход из аккаунта и возврат к окну входа.
        """
        try:
            # Закрываем главное окно
            if self.main_window:
                self.main_window.close()
                self.main_window = None
            
            # Сбрасываем состояние пользователя
            self.model.reset_user()
            
            # Пересоздаём окно входа
            self._create_login_window()
            
            # Показываем окно входа
            self.login_window.show()
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                None, 
                "Ошибка", 
                f"Не удалось вернуться к окну входа:\n{e}"
            )
    
    def shutdown(self):
        """
        Полное завершение работы приложения.
        Вызывается при закрытии приложения.
        """
        try:
            # Закрываем все окна
            if self.main_window:
                self.main_window.close()
            if self.login_window:
                self.login_window.close()
            
            # Закрываем модель и БД
            if self.model:
                self.model.shutdown()
                
        except Exception as e:
            print(f"Ошибка при завершении приложения: {e}")
            traceback.print_exc()