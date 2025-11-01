import sqlite3
import os


# Класс БД который реализует методы для работы с БД
class DataBase:
    def __init__(self):
        # Инициализируем БД
        self._initialize_tables()

    def _get_connection(self):
        # Подключаемся к БД
        db_path = os.path.join(os.path.dirname(__file__), 'habit_database.db')
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # Метод инициализации бд
    def _initialize_tables(self):
        self._get_connection()
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT        NOT NULL
                            )
                            ''')
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS habits
                            (
                                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id    INTEGER,
                                name       TEXT UNIQUE,
                                category   TEXT,
                                frequency  TEXT,
                                created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
                                marked     INTEGER DEFAULT 0,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            )
                            """)

    def close(self):
        self.connection.close()

    def commit_changes(self):
        self.connection.commit()

    def execute_query_and_commit(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def add_user(self, username, password):
        pass

    def getter(self, query, params):
        return self.connection.execute(query, params).fetchall()

    def getter_for_one(self, query, params):
        return self.connection.execute(query, params).fetchone()

