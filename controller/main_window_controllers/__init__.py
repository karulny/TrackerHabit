from view.main_window import Ui_MainWindow
from .my_habbits_controller import MyHabitsController
from .statistic_controller import StatisticController
from PyQt6.QtWidgets import QMainWindow, QMessageBox


class MainWindowController(QMainWindow, Ui_MainWindow):
    def __init__(self, model=None):
        super().__init__()
        self.setupUi(self)
        self.model = model
        self.habit_controller = MyHabitsController(self, model=self.model)
        # settings_controller = SettingsController(self)
        # self.statistic_controller = StatisticController(self, model=self.model)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выйти', 'Вы точно хотите выйти?', QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.model.close()
            event.accept()
        else:
            event.ignore()
