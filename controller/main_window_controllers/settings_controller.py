from PyQt6.QtWidgets import QMessageBox
import os

class SettingsController:
    def __init__(self, window, model) -> None:
        self.window = window
        self.model = model
        self.init_ui()
        print("шзпаьуш")

    def init_ui(self):
        try:
            self.window.UserNameLabel.setText(f"Имя пользователя: {self.model.user.username}")
        except Exception:
            self.window.UserNameLabel.setText("Ошибка при получении имени пользователя")
                # Установка темы по умолчанию
        if getattr(self.model, "is_dark_mode_enabled", False):
            self.window.DarkUiRadioBtn.setChecked(True)
        else:
            self.window.LightUiRadioBtn.setChecked(True)

        # Смена темы при переключении радио-кнопок
        self.window.UiColorGroup.buttonToggled.connect(self.switch_theme)

        # Применяем текущую тему при запуске
        self.apply_theme("dark" if self.window.DarkUiRadioBtn.isChecked() else "light")

    def switch_theme(self, button, checked):
        """Вызывается при переключении радиокнопок"""
        if not checked:
            return  # чтобы не реагировать на снятие выбора

        theme_name = "dark" if button == self.window.DarkUiRadioBtn else "light"
        self.apply_theme(theme_name)

        # сохраняем выбор пользователя в модель или настройки
        self.model.is_dark_mode_enabled = (theme_name == "dark")

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