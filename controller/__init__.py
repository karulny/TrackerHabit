from .main_window_controllers import MainWindowController
from .login_controller import LoginController

class StartUpController:
    def __init__(self):
        self.main_window = MainWindowController()
        # self.login_window = LoginController()
