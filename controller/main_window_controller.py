from view.main_window import Ui_MainWindow
from main_window_controllers.my_habbits_controller import MyHabitsController
from main_window_controllers.settings_controller import SettingsController
from main_window_controllers.statistic_controller import StatisticController
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, model=None):
        super().__init__()
        self.setupUi(self)
        self.model = model
        self.habit_controller = MyHabitsController(self)
        # settings_controller = SettingsController(self)
        # statistic_controller = StatisticController(self)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())