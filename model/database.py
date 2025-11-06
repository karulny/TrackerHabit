import sqlite3

# Класс БД который реализует методы для работы с БД
class DataBase:
    def __init__(self, db_path):
        # Инициализируем БД
        self._initialize_tables(db_path)

    def _get_connection(self, db_path):
        # Подключаемся к БД
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # Метод инициализации бд
    def _initialize_tables(self, db_path):
        self._get_connection(db_path)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT        NOT NULL,
                last_login TEXT DEFAULT (date('now')),
                theme    TEXT DEFAULT  dark
            )
        ''')

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                name       TEXT UNIQUE,
                category   TEXT,
                daily_frequency  INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (date('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_progress
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id   INTEGER,
                date       TEXT DEFAULT (datetime('now')),
                progress   INTEGER DEFAULT 0,
                target     INTEGER DEFAULT 1,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )               
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits_progress_monthly
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT DEFAULT (date('now')),
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
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

    def getter(self, query, params):
        return self.connection.execute(query, params).fetchall()

    def getter_for_one(self, query, params):
        return self.connection.execute(query, params).fetchone()

