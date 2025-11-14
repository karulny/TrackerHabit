from .main_window_model import MainWindowModel
from .registrarion_model import AuthModel
from .database import DataBase
import os
import sys


def get_app_data_dir():
    """Возвращает путь к папке данных приложения в зависимости от ОС"""
    if sys.platform == 'win32':
        # Windows: C:\Users\Username\AppData\Local\HabitTracker
        app_data = os.getenv('LOCALAPPDATA')
        app_dir = os.path.join(app_data, 'HabitTracker')
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/HabitTracker
        home = os.path.expanduser('~')
        app_dir = os.path.join(home, 'Library', 'Application Support', 'HabitTracker')
    else:
        # Linux: ~/.local/share/HabitTracker
        home = os.path.expanduser('~')
        app_dir = os.path.join(home, '.local', 'share', 'HabitTracker')
    
    # Создаём папку, если её нет
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


class Model:
    """Объединённая модель, которая даёт доступ к обеим подмоделям."""

    def __init__(self):
        # Получаем правильный путь к базе данных
        app_data_dir = get_app_data_dir()
        db_path = os.path.join(app_data_dir, 'habit_database.db')
        
        print(f"Database path: {db_path}")  # Для отладки
        
        self.database = DataBase(db_path)
        self.user = None
        self.auth = AuthModel(self.database)

    def close(self):
        if self.user:
            self.auth.update_last_login(self.user.user_id)

    def get_auth(self):
        return self.auth

    def init_user(self, user_id):
        self.user = MainWindowModel(self.database, user_id)

    def get_user(self):
        return self.user