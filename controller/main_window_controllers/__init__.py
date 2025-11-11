from view.main_window import Ui_MainWindow
from .my_habbits_controller import MyHabitsController
from .statistic_controller import StatisticController
from .settings_controller import SettingsController
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSignal


class MainWindowController(QMainWindow, Ui_MainWindow):
    unlogin_from_main = pyqtSignal()
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)
        self.model = model
        self.user_model = model.get_user()
        self.auth_model = model.get_auth()
        self.habit_controller = MyHabitsController(self, self.user_model)
        self.statistic_controller = StatisticController(self, self.user_model)
        self.settings_controller = SettingsController(self, self.auth_model, self.user_model)
        self.connect_signal()



    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выйти', 'Вы точно хотите выйти?', QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.model.close()
            event.accept()
        else:
            event.ignore()

    def connect_signal(self):
        self.tabWidget.tabBarClicked.connect(
            self.updater
        )
            # Подключаем сигнал выхода
        self.settings_controller.unlogin.connect(self.handle_unlogin)

    def handle_unlogin(self):
        """Вызывается при сигнале выхода из настроек"""
        reply = QMessageBox.question(self, "Выход", "Вы точно хотите выйти из аккаунта?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            self.user_model.close()
            # Эмитим событие вверх — для StartUpController
            self.unlogin_from_main.emit()  # Можно добавить этот сигнал, если нужно

    def updater(self):
        # обновляем привычки и ТД, а то в друг беда будет
        self.statistic_controller.update_habits()
        self.habit_controller.show_habits()
