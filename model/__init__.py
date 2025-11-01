from .main_window_model import MainWindowModel
from .registrarion_model import AuthModel
from .database import DataBase

class Model:
    """Объединённая модель, которая даёт доступ к обеим подмоделям."""

    def __init__(self):
        self.database = DataBase()
        self.user = MainWindowModel(self.database)
        self.auth = AuthModel(self.database)

    def close(self):
        self.user.close()

    def get_auth(self):
        return self.auth

    def get_user(self):
        return self.user