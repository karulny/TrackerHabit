import sqlite3
import json
from datetime import datetime, date
from typing import Optional
import os
import hashlib


class DatabaseQueries:
    """Класс с SQL запросами"""
    
    # ========== Запросы для импорта/экспорта ==========
    GET_USER_THEME = 'SELECT theme FROM users WHERE id = ?'
    GET_USER_HABITS = 'SELECT * FROM habits WHERE user_id = ?'
    GET_HABIT_PROGRESS = 'SELECT * FROM habit_progress WHERE habit_id IN ({})'
    GET_MONTHLY_PROGRESS = 'SELECT * FROM habits_progress_monthly WHERE habit_id IN ({})'
    
    CHECK_USER_EXISTS = 'SELECT id FROM users WHERE id = ?'
    UPDATE_USER_THEME = 'UPDATE users SET theme = ? WHERE id = ?'
    
    DELETE_USER_MONTHLY_PROGRESS = '''
        DELETE FROM habits_progress_monthly 
        WHERE habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    '''
    DELETE_USER_HABIT_PROGRESS = '''
        DELETE FROM habit_progress 
        WHERE habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    '''
    DELETE_USER_HABITS = 'DELETE FROM habits WHERE user_id = ?'
    
    INSERT_HABIT = '''
        INSERT INTO habits (user_id, name, category, daily_frequency, created_at)
        VALUES (?, ?, ?, ?, ?)
    '''
    INSERT_HABIT_PROGRESS = '''
        INSERT INTO habit_progress (habit_id, date, progress, target)
        VALUES (?, ?, ?, ?)
    '''
    INSERT_MONTHLY_PROGRESS = '''
        INSERT INTO habits_progress_monthly (habit_id, date, completed)
        VALUES (?, ?, ?)
    '''
    
    # ========== Запросы для MainWindowModel ==========
    ADD_HABIT_PROGRESS = """
        INSERT INTO habit_progress (habit_id, date, progress, target)
        VALUES (?, datetime('now','localtime'), ?, ?);
    """
    
    GET_LAST_TODAY_PROGRESS = """
        SELECT progress, target
        FROM habit_progress
        WHERE habit_id = ? 
        AND date(date) = date('now','localtime')
        ORDER BY id DESC
        LIMIT 1;
    """
    
    CHECK_IF_TODAY_MONTHLY_EXISTS = """
        SELECT id
        FROM habits_progress_monthly
        WHERE habit_id = ? AND date = date('now','localtime');
    """
    
    GET_LAST_HABIT_PROGRESS_AND_TARGET = """
        SELECT progress, target
        FROM habit_progress
        WHERE habit_id = ? AND date = date('now','localtime')
        ORDER BY id DESC
        LIMIT 1;
    """
    
    ADD_MONTHLY_PROGRESS = """
        INSERT INTO habits_progress_monthly (habit_id, date, completed)
        VALUES (?, date('now','localtime'), ?);
    """
    
    UPDATE_LAST_HABIT_PROGRESS_MONTHLY = """
        UPDATE habits_progress_monthly
        SET completed = ?
        WHERE habit_id = ? AND date = date('now','localtime');
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
        WHERE date(date) < date('now', 'localtime');
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
    """
    
    GET_HABIT_STATISTIC_FOR_N_DAYS = """
        SELECT completed, date
        FROM habits_progress_monthly
        WHERE habit_id = ?
          AND date >= date('now', '-' || ? || ' days')
        ORDER BY date ASC;
    """
    
    DELETE_OLD_MONTHLY_PROGRESS = """
        DELETE FROM habits_progress_monthly
        WHERE date < date('now', '-30 days');
    """
    
    # ========== Запросы для AuthModel ==========
    INSERT_USER = "INSERT INTO users (username, password) VALUES (?, ?)"
    
    GET_PASSWORD_ON_USERNAME = "SELECT password FROM users WHERE username = ?"
    
    GET_ID_ON_USERNAME = "SELECT id FROM users WHERE username = ?"
    
    UPDATE_LAST_LOGIN_QUERY = """
        UPDATE users 
        SET last_login = DATE('now') 
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

    def getter_for_one(self, query, params=()):
        cur = self.connection.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        if row is None:
            return None
        return dict(row)
    
    # ========== Методы импорта/экспорта ==========
    
    def export_user_data(self, user_id: int, output_file: str) -> bool:
        """
        Экспортировать привычки и тему пользователя в JSON
        
        Args:
            user_id: ID пользователя
            output_file: Путь к выходному JSON файлу
        
        Returns:
            True если экспорт успешен
        """
        try:
            # Получаем тему пользователя
            self.cursor.execute(self.GET_USER_THEME, (user_id,))
            user = self.cursor.fetchone()
            
            if not user:
                print(f"✗ Пользователь с ID {user_id} не найден")
                return False
            
            # Получаем привычки пользователя
            self.cursor.execute(self.GET_USER_HABITS, (user_id,))
            habits = self.cursor.fetchall()
            
            # Получаем ID привычек
            habit_ids = [h[0] for h in habits]
            
            # Получаем прогресс для привычек
            habit_progress = []
            monthly_progress = []
            
            if habit_ids:
                placeholders = ','.join('?' * len(habit_ids))
                
                query = self.GET_HABIT_PROGRESS.format(placeholders)
                self.cursor.execute(query, habit_ids)
                habit_progress = self.cursor.fetchall()
                
                query = self.GET_MONTHLY_PROGRESS.format(placeholders)
                self.cursor.execute(query, habit_ids)
                monthly_progress = self.cursor.fetchall()
            
            # Формируем структуру данных
            export_data = {
                'export_date': datetime.now().isoformat(),
                'version': '1.0',
                'theme': user[0] if user else 'dark',
                'habits': [],
                'habit_progress': [],
                'habits_progress_monthly': []
            }
            
            # Конвертируем привычки
            for habit in habits:
                export_data['habits'].append({
                    'id': habit[0],
                    'name': habit[2],
                    'category': habit[3],
                    'daily_frequency': habit[4],
                    'created_at': habit[5]
                })
            
            # Конвертируем прогресс
            for progress in habit_progress:
                export_data['habit_progress'].append({
                    'habit_id': progress[1],
                    'date': progress[2],
                    'progress': progress[3],
                    'target': progress[4]
                })
            
            # Конвертируем месячный прогресс
            for monthly in monthly_progress:
                export_data['habits_progress_monthly'].append({
                    'habit_id': monthly[1],
                    'date': monthly[2],
                    'completed': monthly[3]
                })
            
            # Записываем в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Экспорт завершен: {output_file}")
            print(f"  Тема: {export_data['theme']}")
            print(f"  Привычек: {len(export_data['habits'])}")
            print(f"  Записей прогресса: {len(export_data['habit_progress'])}")
            print(f"  Месячных записей: {len(export_data['habits_progress_monthly'])}")
            
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при экспорте: {e}")
            return False
    
    def import_user_data(self, user_id: int, input_file: str, replace_habits: bool = False) -> bool:
        """
        Импортировать привычки и тему для пользователя из JSON
        
        Args:
            user_id: ID пользователя
            input_file: Путь к JSON файлу
            replace_habits: Если True - удаляет существующие привычки перед импортом
        
        Returns:
            True если импорт успешен
        """
        try:
            # Проверяем существование пользователя
            self.cursor.execute(self.CHECK_USER_EXISTS, (user_id,))
            if not self.cursor.fetchone():
                print(f"✗ Пользователь с ID {user_id} не найден")
                return False
            
            # Читаем JSON файл
            with open(input_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Импортируем тему
            theme = import_data.get('theme', 'dark')
            self.cursor.execute(self.UPDATE_USER_THEME, (theme, user_id))
            print(f"✓ Тема обновлена: {theme}")
            
            # Если нужно удалить существующие привычки
            if replace_habits:
                self.cursor.execute(self.DELETE_USER_MONTHLY_PROGRESS, (user_id,))
                self.cursor.execute(self.DELETE_USER_HABIT_PROGRESS, (user_id,))
                self.cursor.execute(self.DELETE_USER_HABITS, (user_id,))
                print("✓ Существующие привычки удалены")
            
            # Карта старых ID привычек к новым
            habit_id_map = {}
            
            # Импортируем привычки
            habits_imported = 0
            for habit in import_data.get('habits', []):
                old_habit_id = habit['id']
                
                try:
                    self.cursor.execute(self.INSERT_HABIT, 
                        (user_id, habit['name'], habit.get('category'), 
                         habit.get('daily_frequency', 0), habit.get('created_at')))
                    
                    new_habit_id = self.cursor.lastrowid
                    habit_id_map[old_habit_id] = new_habit_id
                    habits_imported += 1
                    
                except Exception as e:
                    print(f"⚠ Пропущена привычка '{habit['name']}': {e}")
            
            # Импортируем прогресс
            progress_imported = 0
            for progress in import_data.get('habit_progress', []):
                old_habit_id = progress['habit_id']
                
                if old_habit_id not in habit_id_map:
                    continue
                
                new_habit_id = habit_id_map[old_habit_id]
                
                try:
                    self.cursor.execute(self.INSERT_HABIT_PROGRESS,
                        (new_habit_id, progress.get('date'), 
                         progress.get('progress', 0), progress.get('target', 1)))
                    progress_imported += 1
                except Exception:
                    pass
            
            # Импортируем месячный прогресс
            monthly_imported = 0
            for monthly in import_data.get('habits_progress_monthly', []):
                old_habit_id = monthly['habit_id']
                
                if old_habit_id not in habit_id_map:
                    continue
                
                new_habit_id = habit_id_map[old_habit_id]
                
                try:
                    self.cursor.execute(self.INSERT_MONTHLY_PROGRESS,
                        (new_habit_id, monthly.get('date'), monthly.get('completed', 0)))
                    monthly_imported += 1
                except Exception:
                    pass
            
            self.connection.commit()
            
            print(f"\n✓ Импорт завершен!")
            print(f"  Привычек импортировано: {habits_imported}")
            print(f"  Записей прогресса: {progress_imported}")
            print(f"  Месячных записей: {monthly_imported}")
            
            return True
            
        except FileNotFoundError:
            print(f"✗ Файл не найден: {input_file}")
            return False
        except json.JSONDecodeError:
            print(f"✗ Ошибка чтения JSON файла")
            return False
        except Exception as e:
            print(f"✗ Ошибка при импорте: {e}")
            self.connection.rollback()
            return False
    
    def create_backup(self, user_id: int, backup_dir: str = 'backups') -> Optional[str]:
        """
        Создать резервную копию данных пользователя
        
        Args:
            user_id: ID пользователя
            backup_dir: Директория для бэкапов
        
        Returns:
            Путь к файлу бэкапа или None при ошибке
        """
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'habits_backup_user{user_id}_{timestamp}.json')
            
            if self.export_user_data(user_id, backup_file):
                print(f"✓ Бэкап создан: {backup_file}")
                return backup_file
            return None
            
        except Exception as e:
            print(f"✗ Ошибка создания бэкапа: {e}")
            return None
    
    def restore_from_backup(self, user_id: int, backup_file: str, replace_habits: bool = True) -> bool:
        """
        Восстановить данные из бэкапа
        
        Args:
            user_id: ID пользователя
            backup_file: Путь к файлу бэкапа
            replace_habits: Удалить существующие привычки
        
        Returns:
            True если восстановление успешно
        """
        print(f"→ Восстановление из бэкапа: {backup_file}")
        return self.import_user_data(user_id, backup_file, replace_habits)