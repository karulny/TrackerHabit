from .main_window_model import MainWindowModel
from .registrarion_model import AuthModel
from .database import DataBase

class Model:
    """Объединённая модель, которая даёт доступ к обеим подмоделям."""

    def __init__(self):
        self.database = DataBase()
        self.user = MainWindowModel(1, self.database)

    def close(self):
        self.user.close()