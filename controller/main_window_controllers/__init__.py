from view.main_window import Ui_MainWindow
from .my_habbits_controller import MyHabitsController
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from model import Model


class MainWindowController(QMainWindow, Ui_MainWindow):
    def __init__(self, user_id=1):
        super().__init__()
        self.setupUi(self)
        self.model = Model()
        self.user_id = user_id
        self.habit_controller = MyHabitsController(self, user_id=self.user_id, model=self.model.user)
        # settings_controller = SettingsController(self)
        # statistic_controller = StatisticController(self)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выйти', 'Вы точно хотите выйти?', QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.model.close()
            event.accept()
        else:
            event.ignore()