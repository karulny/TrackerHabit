from view.main_window import Ui_MainWindow
from .my_habbits_controller import MyHabitsController
from PyQt6.QtWidgets import QMainWindow, QMessageBox


class MainWindowController(QMainWindow, Ui_MainWindow):
    def __init__(self, user_id=0, model=None):
        super().__init__()
        self.setupUi(self)
        self.model = model
        self.user_id = user_id
        self.habit_controller = MyHabitsController(self, user_id=self.user_id, model=self.model)
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
