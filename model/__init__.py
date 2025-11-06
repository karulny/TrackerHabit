from .main_window_model import MainWindowModel
from .registrarion_model import AuthModel
from .database import DataBase
import os

class Model:
    """Объединённая модель, которая даёт доступ к обеим подмоделям."""

    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'habit_database.db')
        self.database = DataBase(db_path)
        self.user = None
        self.auth = AuthModel(self.database)

    def close(self):
        self.auth.update_last_login(self.user.user_id)
        self.user.close()

    def get_auth(self):
        return self.auth

    def init_user(self, user_id):
        self.user = MainWindowModel(self.database, user_id)
    
    def get_user(self):
        return self.user