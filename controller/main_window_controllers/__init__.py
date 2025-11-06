from view.main_window import Ui_MainWindow
from .my_habbits_controller import MyHabitsController
from .statistic_controller import StatisticController
from .settings_controller import SettingsController
from PyQt6.QtWidgets import QMainWindow, QMessageBox


class MainWindowController(QMainWindow, Ui_MainWindow):
    def __init__(self, model, user_id):
        super().__init__()
        self.setupUi(self)
        self.user_model = model.get_user()
        self.auth_model = model.get_auth()
        self.habit_controller = MyHabitsController(self, self.user_model)
        self.statistic_controller = StatisticController(self, self.user_model)
        self.settings_controller = SettingsController(self, self.auth_model, self.user_model.user_id)
        self.connect_signal()



    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выйти', 'Вы точно хотите выйти?', QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.user_model.close()
            event.accept()
        else:
            event.ignore()

    def connect_signal(self):
        self.tabWidget.tabBarClicked.connect(
            self.statistic_controller.update_habits
        )