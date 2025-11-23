from PyQt6.QtWidgets import QMessageBox, QLineEdit, QFileDialog
from PyQt6.QtCore import pyqtSignal, QObject
import os


class SettingsController(QObject):
    """Контроллер вкладки настроек. Здесь наследуемся от Qobject чтобы сделать сигнал"""
    unlogin = pyqtSignal()

    def __init__(self, window, model, user_model) -> None:
        super().__init__()
        self.window = window
        self.auth_model = model
        self.user_model = user_model
        self.init_ui()

    def init_ui(self):
        # Подключаем кнопки
        self.window.UnloginBrn.clicked.connect(self.exit_btn)
        self.window.ShowPwd.clicked.connect(self.show_password)
        self.window.ChangePasswordBtn.clicked.connect(self.change_password_btn)
        self.window.ResetBtn.clicked.connect(self.reset_btn)
        self.window.ImportProfileBtn.clicked.connect(self.import_btn)
        self.window.ExportProfileBtn.clicked.connect(self.export_btn)


        # Вывод имени пользователя
        try:
            self.window.UserNameLabel.setText(f"Имя пользователя: {self.auth_model.username}")
        except Exception:
            self.window.UserNameLabel.setText("Ошибка при получении имени пользователя")

        # Установка темы пользователя        
        if self.auth_model.get_theme() == "dark":
            self.window.DarkUiRadioBtn.setChecked(True)
        else:
            self.window.LightUiRadioBtn.setChecked(True)

        # Смена темы при переключении радио-кнопок
        self.window.UiColorGroup.buttonToggled.connect(self.switch_theme)

        # Применяем текущую тему при запуске
        self.apply_theme(self.auth_model.get_theme().strip())

    def switch_theme(self, button, checked):
        """Вызывается при переключении радиокнопок"""
        if not checked:
            return  # чтобы не реагировать на снятие выбора

        theme_name = "dark" if button == self.window.DarkUiRadioBtn else "light"
        self.apply_theme(theme_name)
        self.auth_model.save_user_theme(theme_name)

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

    def show_password(self):
        current_mode = self.window.RegistPasswordEdit.echoMode()

        if current_mode == QLineEdit.EchoMode.Password:
            self.window.RegistPasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.window.RegistPasswordConfirmEdit.setEchoMode(QLineEdit.EchoMode.Normal)

            self.window.ShowPwd.setText("🙈")
        else:
            self.window.RegistPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.window.RegistPasswordConfirmEdit.setEchoMode(QLineEdit.EchoMode.Password)

            self.window.ShowPwd.setText("👁")

    def change_password_btn(self):
            """Обработчик смены пароля с валидацией и очисткой полей"""
            password = self.window.RegistPasswordEdit.text().strip()
            confirm_pass = self.window.RegistPasswordConfirmEdit.text().strip()
            
            # Проверка на пустые поля
            if not password or not confirm_pass:
                QMessageBox.warning(self.window, "Ошибка", "Заполните оба поля для смены пароля")
                return
            
            # Проверка длины пароля
            if len(password) < 6:
                QMessageBox.warning(self.window, "Ошибка", "Пароль должен быть не менее 6 символов")
                return
            
            # Проверка совпадения паролей
            if password != confirm_pass:
                QMessageBox.warning(self.window, "Ошибка", "Пароли не совпадают")
                return
            
            # Все проверки пройдены - меняем пароль
            try:
                self.auth_model.change_password(password)
                QMessageBox.information(self.window, "Успешно", "Пароль успешно изменен")
                
                # Очищаем поля после успешной смены
                self.window.RegistPasswordEdit.clear()
                self.window.RegistPasswordConfirmEdit.clear()
                
            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f"Не удалось изменить пароль:\n{e}")

    def reset_btn(self):
        """Сброс всех данных пользователя с подтверждением"""
        reply = QMessageBox.question(
            self.window, 
            'Подтверждение сброса', 
            'ВСЕ ВАШИ ПРИВЫЧКИ И ПРОГРЕСС БУДУТ БЕЗВОЗВРАТНО УДАЛЕНЫ!\n\nВы уверены, что хотите продолжить?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # По умолчанию выбрана кнопка "Нет"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.user_model.reset_data()
                QMessageBox.information(
                    self.window, 
                    "Успешно", 
                    "Все данные успешно удалены"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self.window, 
                    "Ошибка", 
                    f"Не удалось удалить данные:\n{e}"
                )

    def import_btn(self):
        """Функция для импорта привычек из JSON файла"""
        try:
            # Получаем путь json массива с привычками
            file_path = QFileDialog.getOpenFileName(
                self.window, 
                "Выберите файл для импорта",
                "",
                "JSON Files (*.json)"
            )[0]
            
            # Если пользователь отменил выбор файла
            if not file_path:
                return
            
            # Импортируем привычки
            imported, skipped = self.user_model.import_habits(file_path)
            
            # Формируем сообщение о результатах
            message = f"Импорт завершен!\n\n"
            message += f"✅ Импортировано: {imported}\n"
            
            if skipped > 0:
                message += f"⚠️ Пропущено (дубликаты): {skipped}"
            
            QMessageBox.information(self.window, "Успешно", message)
            
            # Обновляем отображение привычек
            if hasattr(self.window, 'habit_controller'):
                self.window.habit_controller.show_habits()

        except FileNotFoundError:
            QMessageBox.warning(self.window, "Ошибка", "Файл не найден")
        
        except ValueError as e:
            QMessageBox.warning(self.window, "Ошибка", str(e))
        
        except Exception as e:
            QMessageBox.critical(
                self.window, 
                "Ошибка", 
                f"Произошла ошибка при импорте:\n{e}"
            )

    def export_btn(self):
        """Функция для экспорта привычек в JSON файл"""
        try:
            # Получаем путь json массива с привычками, тк .getSaveFileName вернет корртеж где первый элемент — путь то берем только его 
            file_path = QFileDialog.getSaveFileName(self.window, filter="JSON Files (*.json)")[0]
            # А теперь модели даем наш путь чтобы она все сделала
            self.user_model.export_habits(file_path)

        except Exception as e:
            QMessageBox.warning(self.window, "Ошибка", f"Произошла ошибка: {e}")

        else:
            QMessageBox.information(self.window, "Успешно", "Привычки успешно экспортированы.")

