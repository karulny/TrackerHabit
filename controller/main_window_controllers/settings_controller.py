from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSignal, QObject
import os

class SettingsController(QObject):
    unlogin = pyqtSignal()

    def __init__(self, window, model, user_id) -> None:
        super().__init__()
        self.window = window
        self.model = model
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.window.UnloginBrn.clicked.connect(self.exit_btn)
        try:
            self.window.UserNameLabel.setText(f"Имя пользователя: {self.model.user_id}")
        except Exception:
            self.window.UserNameLabel.setText("Ошибка при получении имени пользователя")
                # Установка темы по умолчанию
        if self.model.get_theme() == "dark":
            self.window.DarkUiRadioBtn.setChecked(True)
        else:
            self.window.LightUiRadioBtn.setChecked(True)

        # Смена темы при переключении радио-кнопок
        self.window.UiColorGroup.buttonToggled.connect(self.switch_theme)

        # Применяем текущую тему при запуске
        print(self.model.get_theme())
        self.apply_theme(self.model.get_theme().strip())

    def switch_theme(self, button, checked):
        """Вызывается при переключении радиокнопок"""
        if not checked:
            return  # чтобы не реагировать на снятие выбора

        theme_name = "dark" if button == self.window.DarkUiRadioBtn else "light"
        self.apply_theme(theme_name)
        self.model.save_user_theme(theme_name)


    def apply_theme(self, theme_name: str):
        """Загружает и применяет .qss тему"""
        try:
            path = os.path.join(os.path.dirname(__file__), "themes")
            print(path)
            theme_file = os.path.join(path, f"{theme_name.strip()}.qss")
            print(theme_file)

            with open(theme_file, 'r', encoding='utf-8') as file:
                style = file.read()
                self.window.setStyleSheet(style)
        except Exception as e:
            QMessageBox.critical(self.window, "Ошибка", f"Не удалось применить тему: {e}")

    def exit_btn(self):
        """Обработчик кнопки выхода"""
        self.unlogin.emit()