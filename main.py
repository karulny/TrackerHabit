from PyQt6.QtWidgets import QApplication
import sys
from controller import StartUpController


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    
    # Создаём главный контроллер
    controller = StartUpController()
    controller.show_login_window()
    
    # Запускаем цикл обработки событий
    exit_code = app.exec()
    
    # При выходе из приложения корректно закрываем всё
    controller.shutdown()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()