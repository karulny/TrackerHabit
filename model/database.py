import sqlite3


class DatabaseQueries:
    """Класс с SQL запросами"""
    
    # ========== Запросы для импорта/экспорта ==========
    GET_USER_HABITS = 'SELECT * FROM habits WHERE user_id = ?'
    
    # Отдельный метод нужен чтобы не потерять время
    INSERT_IMPORTED_HABIT = """
        INSERT INTO habits (user_id, name, category, daily_frequency, created_at)
        VALUES (?, ?, ?, ?, ?)
    """
    
    # ========== Запросы для MainWindowModel ==========
    ADD_HABIT_PROGRESS = """
        INSERT INTO habit_progress (habit_id, date, progress, target)
        VALUES (?, datetime('now', 'localtime'), ?, ?);
    """
    
    GET_LAST_TODAY_PROGRESS = """
        SELECT progress, target
        FROM habit_progress
        WHERE habit_id = ? 
        AND date(date, 'localtime') = date('now', 'localtime')
        ORDER BY id DESC
        LIMIT 1;
    """
    
    CHECK_IF_TODAY_MONTHLY_EXISTS = """
        SELECT id
        FROM habits_progress_monthly
        WHERE habit_id = ? AND date = date('now', 'localtime');
    """
    
    GET_LAST_HABIT_PROGRESS_AND_TARGET = """
        SELECT progress, target
        FROM habit_progress
        WHERE habit_id = ? AND date(date, 'localtime') = date('now', 'localtime')
        ORDER BY id DESC
        LIMIT 1;
    """
    
    ADD_MONTHLY_PROGRESS = """
        INSERT INTO habits_progress_monthly (habit_id, date, completed)
        VALUES (?, date('now', 'localtime'), ?);
    """
    
    UPDATE_LAST_HABIT_PROGRESS_MONTHLY = """
        UPDATE habits_progress_monthly
        SET completed = ?
        WHERE habit_id = ? AND date = date('now', 'localtime');
    """
    
    GET_HABIT_TARGET = """
        SELECT daily_frequency
        FROM habits
        WHERE id = ?;
    """
    
    INSERT_HABIT_QUERY = """
        INSERT INTO habits (user_id, name, category, daily_frequency)
        VALUES (?, ?, ?, ?)
    """
    
    SELECT_HABITS_QUERY = """
        SELECT *
        FROM habits
        WHERE user_id = ?
    """
    
    SELECT_CATEGORIES_QUERY = """
        SELECT DISTINCT category
        FROM habits
        WHERE user_id = ?
    """
    
    RESET_DAILY_PROGRESS = """
        DELETE FROM habit_progress
        WHERE date(date, 'localtime') < date('now', 'localtime');
    """
    
    IS_HABIT_COMPLETED_TODAY = """
        SELECT progress, target
        FROM habit_progress
        WHERE habit_id = ?
        ORDER BY id DESC
        LIMIT 1
    """
    
    DELETE_HABIT_PROGRESS = """
        DELETE FROM habit_progress
        WHERE habit_id = ?
    """
    
    DELETE_HABIT_PROGRESS_MONTHLY_QUERY = """
        DELETE FROM habits_progress_monthly
        WHERE habit_id = ?;
    """
    
    DELETE_HABITS = "DELETE FROM habits WHERE user_id = ?"
    
    DELETE_HABIT_QUERY = """
        DELETE FROM habits
        WHERE user_id = ? AND name = ?;
    """
    
    GET_HABIT_ID_QUERY = """
        SELECT id
        FROM habits
        WHERE user_id = ? AND name = ?
    """
    
    GET_LAST_DATE_QUERY = """
        SELECT last_login AS date
        FROM users
        WHERE id = ?
        ORDER BY date DESC
        LIMIT 1
    """
    
    GET_DAILY_PROGRESS = """
        SELECT date, progress
        FROM habit_progress
        WHERE habit_id = ?
        AND date(date, 'localtime') = date('now', 'localtime')
        ORDER BY date ASC;
    """
    
    GET_HABIT_STATISTIC_FOR_N_DAYS = """
        SELECT completed, date
        FROM habits_progress_monthly
        WHERE habit_id = ?
          AND date >= date('now', 'localtime', '-' || ? || ' days')
        ORDER BY date ASC;
    """
    
    DELETE_OLD_MONTHLY_PROGRESS = """
        DELETE FROM habits_progress_monthly
        WHERE date < date('now', 'localtime', '-30 days');
    """
    
    # ========== Запросы для AuthModel ==========
    INSERT_USER = "INSERT INTO users (username, password) VALUES (?, ?)"
    
    GET_PASSWORD_ON_USERNAME = "SELECT password FROM users WHERE username = ?"
    
    GET_ID_ON_USERNAME = "SELECT id FROM users WHERE username = ?"
    
    UPDATE_LAST_LOGIN_QUERY = """
        UPDATE users 
        SET last_login = date('now', 'localtime') 
        WHERE id = ?
    """
    
    GET_THEME_OF_USER = """
        SELECT theme
        FROM users 
        WHERE username = ?
    """
    
    SET_THEME = """
        UPDATE users
        SET theme = ?
        WHERE username = ?
    """
    
    CHANGE_PASSWORD = """
        UPDATE users
        SET password = ?
        WHERE username = ?
    """

    # ======= Запросы для инициализации таблицы

    SQL_INIT_USER_TABLE = """
            CREATE TABLE IF NOT EXISTS users
            (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT        NOT NULL,
                last_login TEXT DEFAULT (date('now', 'localtime')),
                theme    TEXT DEFAULT 'dark'
            )
        """
    SQL_INIT_HABITS_TABLE = """
            CREATE TABLE IF NOT EXISTS habits
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                name       TEXT UNIQUE,
                category   TEXT,
                daily_frequency  INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (date('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        
    SQL_INIT_HABITS_PROGRESS_TABLE = """
            CREATE TABLE IF NOT EXISTS habit_progress
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id   INTEGER,
                date       TEXT DEFAULT (datetime('now', 'localtime')),
                progress   INTEGER DEFAULT 0,
                target     INTEGER DEFAULT 1,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )               
        """
    
    SQL_INIT_HABITS_MONTHLY_PROGRESS_TABLE = """
            CREATE TABLE IF NOT EXISTS habits_progress_monthly
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT DEFAULT (date('now', 'localtime')),
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )  
        """

class DataBase(DatabaseQueries):
    """Класс БД который реализует методы для работы с БД"""
    
    def __init__(self, db_path):
        super().__init__()
        self._initialize_tables(db_path)

    def _get_connection(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def _initialize_tables(self, db_path):
        self._get_connection(db_path)
        self.cursor.execute(self.SQL_INIT_USER_TABLE)

        self.cursor.execute(self.SQL_INIT_HABITS_TABLE)

        self.cursor.execute(self.SQL_INIT_HABITS_PROGRESS_TABLE)

        self.cursor.execute(self.SQL_INIT_HABITS_MONTHLY_PROGRESS_TABLE)
        
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных"""
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.close()
                self.connection = None
            except Exception as e:
                print(f"Ошибка при закрытии БД: {e}")

    def is_connected(self):
        """Проверяет, активно ли соединение с БД"""
        return hasattr(self, 'connection') and self.connection is not None

    def commit_changes(self):
        """Сохраняет изменения в БД"""
        if self.is_connected():
            self.connection.commit()

    def execute_query_and_commit(self, query, params=()):
        """Выполняет запрос и сохраняет изменения"""
        if not self.is_connected():
            raise sqlite3.ProgrammingError("Database connection is closed")
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query, params=()):
        """Функция которая выполняет запросы обычно типа GET и ловит все элементы"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def getter_for_one(self, query, params=()):
        """Функция схожая по функционалу с fetch_all, но для одного ряда"""
        cur = self.connection.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        if row is None:
            return None
        return dict(row)