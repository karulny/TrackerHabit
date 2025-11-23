from datetime import date, datetime
import json


class MainWindowModel:
    """Модель главного окна для работы с привычками"""

    def __init__(self, data, user_id):
        self.db = data
        self.user_id = user_id
        # Сохраняем дату последней проверки
        self.last_check_date = None  
        
        if self.today_is_new_day():
            self.reset_daily_progress()
        self.cleanup_old_monthly_progress()

    def add_habit(self, name, category, frequency):
        params = (self.user_id, name, category, frequency)
        self.db.execute_query_and_commit(self.db.INSERT_HABIT_QUERY, params)
        habit_id = self.get_habit_id(name)

        progress_params = (habit_id, 0, frequency)
        self.db.execute_query_and_commit(self.db.ADD_HABIT_PROGRESS, progress_params)

        # Добавляем запись в monthly, только если её нет
        exists = self.db.getter_for_one(self.db.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
        if not exists:
            monthly_params = (habit_id, 0)
            self.db.execute_query_and_commit(self.db.ADD_MONTHLY_PROGRESS, monthly_params)

    def get_habits(self):
        """Возвращает привычки и категории"""
        params = (self.user_id,)
        return self.db.fetch_all(self.db.SELECT_HABITS_QUERY, params)

    def toggle_mark_habit(self, habit_name):
        """
        Добавляет новую строку в habit_progress и увеличивает progress на +1
        относительно последнего значения за сегодня.
        Если цель достигнута — отмечает completed = 1 в habits_progress_monthly.
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return

        # Получаем последнюю запись за сегодня
        last_row = self.db.getter_for_one(self.db.GET_LAST_TODAY_PROGRESS, (habit_id,))

        # Получаем целевой daily_frequency
        target_row = self.db.getter_for_one(self.db.GET_HABIT_TARGET, (habit_id,))
        target = target_row["daily_frequency"] if target_row else 1

        if last_row:
            new_progress = last_row["progress"] + 1
        else:
            new_progress = 1  # если сегодня нет записей, начинаем с 1

        # Добавляем новую строку с текущим временем
        params = (habit_id, new_progress, target)

        self.db.execute_query_and_commit(self.db.ADD_HABIT_PROGRESS, params)

        # Если достигнута цель — обновляем/добавляем запись в monthly
        if new_progress >= target:
            exists = self.db.getter_for_one(self.db.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
            if exists:
                self.db.execute_query_and_commit(self.db.UPDATE_LAST_HABIT_PROGRESS_MONTHLY, (1, habit_id))
            else:
                self.db.execute_query_and_commit(self.db.ADD_MONTHLY_PROGRESS, (habit_id, 1))

    def get_progress_and_target(self, habit_name: str) -> tuple:
        """
        Возвращает (progress, target) последней записи за сегодня.
        Если записей за сегодня нет — возвращает (0, daily_frequency).
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return 0, 0

        row = self.db.getter_for_one(self.db.GET_LAST_TODAY_PROGRESS, (habit_id,))
        if row:
            return row["progress"], row["target"]

        # Если записей нет — возвращаем 0 и target из таблицы habits
        tgt_row = self.db.getter_for_one(self.db.GET_HABIT_TARGET, (habit_id,))
        target = tgt_row['daily_frequency'] if tgt_row else 1
        return 0, target

    def get_categories(self):
        """Возвращает все категории, которые существуют"""
        params = (self.user_id,)
        categories = self.db.fetch_all(self.db.SELECT_CATEGORIES_QUERY, params)
        return [row['category'] for row in categories]

    def remove_habit(self, habit_name):
        """Удаляет привычку"""
        habit_id = self.get_habit_id(habit_name)
        params = (self.user_id, habit_name)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS, (habit_id,))
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, (habit_id,))
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_QUERY, params)

    def is_habit_completed_today(self, habit_name):
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return False

        row = self.db.getter_for_one(self.db.GET_LAST_TODAY_PROGRESS, (habit_id,))
        if row:
            return row.get('progress', 0) >= row.get('target', 0)
        return False

    def reset_daily_progress(self):
        """Сбрасывает ежедневный прогресс для всех привычек"""
        self.db.execute_query_and_commit(self.db.RESET_DAILY_PROGRESS)
        self.init_new_progress_for_habits()
        # Обновляем дату последней проверки
        self.last_check_date = date.today()

    def get_habit_id(self, habit_name):
        """Получает ID привычки по её названию"""
        params = (self.user_id, habit_name)
        row = self.db.getter_for_one(self.db.GET_HABIT_ID_QUERY, params)
        return row['id'] if row else None

    def today_is_new_day(self):
        """Проверяет, является ли сегодня новым днём для сброса прогресса"""
        today = date.today()
        
        # Если уже проверяли сегодня, возвращаем False
        if self.last_check_date == today:
            return False
        
        # Проверяем, есть ли записи за сегодня в habit_progress
        # Если есть хоть одна запись с сегодняшней датой, значит день уже начат
        check_query = """
            SELECT COUNT(*) as count
            FROM habit_progress hp
            JOIN habits h ON hp.habit_id = h.id
            WHERE h.user_id = ? 
            AND date(hp.date) = date('now', 'localtime')
        """
        
        result = self.db.getter_for_one(check_query, (self.user_id,))
        
        if result and result['count'] > 0:
            # Есть записи за сегодня - день уже начат
            self.last_check_date = today
            return False
        
        # Проверяем last_login пользователя
        params = (self.user_id,)
        row = self.db.getter_for_one(self.db.GET_LAST_DATE_QUERY, params)
        
        if row and row['date']:
            try:
                # Парсим дату последнего входа
                last_date_str = row['date']
                # Может быть в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'
                if ' ' in last_date_str:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S").date()
                else:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                
                # Если последний вход был НЕ сегодня - это новый день
                if last_date < today:
                    self.last_check_date = today
                    return True
                    
            except (ValueError, TypeError) as e:
                print(f"Ошибка парсинга даты: {e}")
                # В случае ошибки считаем что это новый день
                self.last_check_date = today
                return True
        
        # Если нет информации о последнем входе - считаем новым днём
        self.last_check_date = today
        return True

    def init_new_progress_for_habits(self):
        """Инициализирует новый прогресс для привычки в начале нового дня"""
        habits_id_and_frequency = [
            (self.get_habit_id(habit["name"]), habit["daily_frequency"])
            for habit in self.get_habits()
        ]
        for habit_id, frequency in habits_id_and_frequency:
            self.db.execute_query_and_commit(self.db.ADD_HABIT_PROGRESS, (habit_id, 0, frequency))

            exists = self.db.getter_for_one(self.db.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
            if not exists:
                self.db.execute_query_and_commit(self.db.ADD_MONTHLY_PROGRESS, (habit_id, 0))

    def get_habit_static_daily(self, habit_name):
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return []

        progress = self.get_progress_and_target(habit_name)[0]

        if progress <= 0:
            return []

        params = (habit_id,)
        rows = self.db.fetch_all(self.db.GET_DAILY_PROGRESS, params)
        return [(row['date'], 1) for row in rows if row and int(row["progress"]) > 0]

    def reset_data(self):
        params = (self.user_id,)
        self.db.execute_query_and_commit(self.db.DELETE_HABITS, params)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS, params)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, params)

    def get_habit_static_for_N_days(self, habit_name, days):
        """
        Возвращает [(дата, выполнено)] за последние N дней
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return []

        try:
            days = int(days)
        except ValueError:
            days = 7

        params = (habit_id, days)
        rows = self.db.fetch_all(self.db.GET_HABIT_STATISTIC_FOR_N_DAYS, params)

        if not rows:
            return []

        return [(row["date"], row["completed"]) for row in rows]

    def cleanup_old_monthly_progress(self):
        """Удаляет записи старше 30 дней из таблицы habits_progress_monthly"""
        self.db.execute_query_and_commit(self.db.DELETE_OLD_MONTHLY_PROGRESS)

    def import_habits(self, file_path):
        """Импортирует привычки из JSON файла, пропуская дубликаты"""
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                habits = json.load(file)
            
            imported_count = 0
            skipped_count = 0
            
            for habit in habits:
                # Проверяем, существует ли уже привычка с таким именем
                if not self.get_habit_id(habit["name"]):
                    try:
                        params = (
                            self.user_id, 
                            habit["name"], 
                            habit["category"], 
                            habit["daily_frequency"], 
                            habit["created_at"]
                        )
                        self.db.execute_query_and_commit(
                            self.db.INSERT_IMPORTED_HABIT, 
                            params
                        )
                        imported_count += 1
                    except Exception as e:
                        print(f"Ошибка при импорте '{habit['name']}': {e}")
                        skipped_count += 1
                else:
                    skipped_count += 1
            
            return imported_count, skipped_count
            
        except FileNotFoundError:
            raise FileNotFoundError("Файл не найден")
        except json.JSONDecodeError:
            raise ValueError("Неверный формат JSON файла")
        except KeyError as e:
            raise ValueError(f"В файле отсутствует обязательное поле: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при импорте: {e}")

    def export_habits(self, file_path):
        params = (self.user_id, )
        habits = self.db.fetch_all(self.db.GET_USER_HABITS, params)
        data = []
        for item in habits:
                habit_progress = self.get_progress_and_target(item["name"])
                habit_entry = {
                    "name": item["name"],
                    "daily_frequency": item["daily_frequency"],
                    "created_at": item["created_at"],
                    "category": item["category"]
                }
                data.append(habit_entry)
        with open(file_path, 'w', encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
    
    def close(self):
        """Закрывает ресурсы модели и очищает кэш"""
        # Очищаем кэшированные данные
        self.last_check_date = None