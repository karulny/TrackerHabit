from datetime import date


class MainWindowModel:
    """
    Модель главного окна для работы с привычками.
    
    Управляет привычками пользователя, отслеживает прогресс выполнения,
    автоматически сбрасывает ежедневный прогресс в новом дне и 
    очищает устаревшие данные.
    """

    def __init__(self, data, user_id):
        """
        Инициализация модели главного окна.
        
        Args:
            data: Объект базы данных (DataBase)
            user_id: ID текущего пользователя
        """
        self.db = data
        self.user_id = user_id
        
        # Проверяем, не начался ли новый день - если да, сбрасываем прогресс
        if self.today_is_new_day():
            self.reset_daily_progress()
        
        # Удаляем старые записи (старше 30 дней)
        self.cleanup_old_monthly_progress()

    def add_habit(self, name, category, frequency):
        """
        Добавляет новую привычку для пользователя.
        
        Создает привычку, инициализирует её начальный прогресс (0)
        и добавляет запись в месячную статистику.
        
        Args:
            name: Название привычки
            category: Категория привычки
            frequency: Целевое количество выполнений в день (daily_frequency)
        """
        params = (self.user_id, name, category, frequency)
        self.db.execute_query_and_commit(self.db.INSERT_HABIT_QUERY, params)
        habit_id = self.get_habit_id(name)

        # Добавляем начальный прогресс (0 из frequency)
        progress_params = (habit_id, 0, frequency)
        self.db.execute_query_and_commit(self.db.ADD_HABIT_PROGRESS, progress_params)

        # Добавляем запись в monthly, только если её нет
        exists = self.db.getter_for_one(self.db.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
        if not exists:
            monthly_params = (habit_id, 0)
            self.db.execute_query_and_commit(self.db.ADD_MONTHLY_PROGRESS, monthly_params)

    def get_habits(self):
        """
        Возвращает все привычки пользователя.
        
        Returns:
            list: Список привычек пользователя в виде sqlite3.Row объектов
        """
        params = (self.user_id,)
        return self.db.getter(self.db.SELECT_HABITS_QUERY, params)

    def toggle_mark_habit(self, habit_name):
        """
        Отмечает выполнение привычки, увеличивая прогресс на +1.
        
        Добавляет новую запись в таблицу habit_progress с увеличенным 
        значением progress. Если достигнута цель (progress >= target),
        автоматически помечает привычку как выполненную в месячной статистике.
        
        Args:
            habit_name: Название привычки
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

    def get_progress_and_target(self, habit_name):
        """
        Возвращает текущий прогресс и цель привычки за сегодня.
        
        Args:
            habit_name: Название привычки
            
        Returns:
            tuple: (progress, target) - текущий прогресс и целевое значение.
                   Если записей за сегодня нет, возвращает (0, daily_frequency)
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
        """
        Возвращает список всех уникальных категорий привычек пользователя.
        
        Returns:
            list: Список строк с названиями категорий
        """
        params = (self.user_id,)
        categories = self.db.getter(self.db.SELECT_CATEGORIES_QUERY, params)
        return [row['category'] for row in categories]

    def remove_habit(self, habit_name):
        """
        Удаляет привычку и все связанные с ней данные.
        
        Удаляет саму привычку, весь её прогресс из habit_progress
        и месячную статистику из habits_progress_monthly.
        
        Args:
            habit_name: Название привычки
        """
        habit_id = self.get_habit_id(habit_name)
        params = (self.user_id, habit_name)
        
        # Удаляем в правильном порядке (сначала зависимые записи)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS, (habit_id,))
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, (habit_id,))
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_QUERY, params)

    def is_habit_completed_today(self, habit_name):
        """
        Проверяет, выполнена ли привычка сегодня.
        
        Привычка считается выполненной, если текущий прогресс
        больше или равен целевому значению (progress >= target).
        
        Args:
            habit_name: Название привычки
            
        Returns:
            bool: True если привычка выполнена, False в противном случае
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return False

        row = self.db.getter_for_one(self.db.GET_LAST_TODAY_PROGRESS, (habit_id,))
        if row:
            return row.get('progress', 0) >= row.get('target', 0)
        return False
    
    def reset_daily_progress(self):
        """
        Сбрасывает ежедневный прогресс всех привычек.
        
        Удаляет все записи прогресса за предыдущие дни и
        инициализирует новый прогресс для всех привычек пользователя
        с начальными значениями (progress=0).
        """
        self.db.execute_query_and_commit(self.db.RESET_DAILY_PROGRESS)
        self.init_new_progress_for_habits()

    def get_habit_id(self, habit_name):
        """
        Получает ID привычки по её названию.
        
        Args:
            habit_name: Название привычки
            
        Returns:
            int или None: ID привычки, или None если привычка не найдена
        """
        params = (self.user_id, habit_name)
        row = self.db.getter_for_one(self.db.GET_HABIT_ID_QUERY, params)
        return row['id'] if row else None

    def today_is_new_day(self):
        """
        Проверяет, начался ли новый день для сброса прогресса.
        
        Сравнивает дату последнего входа пользователя с сегодняшней датой.
        Если даты отличаются - значит начался новый день.
        
        Returns:
            bool: True если начался новый день, False в противном случае
        """
        today = date.today().isoformat()
        params = (self.user_id,)
        row = self.db.getter_for_one(self.db.GET_LAST_DATE_QUERY, params)
        
        if row and row['date'] < today:
            return True
        return False

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
        """
        Получает ежедневную статистику привычки.
        
        Возвращает все даты, когда привычка была отмечена (progress > 0).
        Используется для отображения на графике.
        
        Args:
            habit_name: Название привычки
            
        Returns:
            list: Список кортежей [(дата, 1), ...] где 1 означает наличие прогресса.
                  Возвращает пустой список если привычка не найдена или прогресс = 0
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return []

        progress = self.get_progress_and_target(habit_name)[0]

        if progress <= 0:
            return []  # возвращаем пустой список — график не строится

        params = (habit_id,)
        rows = self.db.getter(self.db.GET_DAILY_PROGRESS, params)
        return [(row['date'], 1) for row in rows if row and int(row["progress"]) > 0]

    def reset_data(self):
        """
        Полностью удаляет все привычки и данные пользователя.
        
        Удаляет:
        - Все привычки пользователя
        - Весь прогресс по привычкам
        - Всю месячную статистику
        
        Используется для полного сброса данных пользователя.
        """
        params = (self.user_id,)
        self.db.execute_query_and_commit(self.db.DELETE_HABITS, params)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS, params)
        self.db.execute_query_and_commit(self.db.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, params)

    def get_habit_static_for_N_days(self, habit_name, days):
        """
        Возвращает статистику выполнения привычки за последние N дней.
        
        Получает данные из месячной статистики (habits_progress_monthly),
        где completed=1 означает что привычка была выполнена в этот день.
        
        Args:
            habit_name: Название привычки
            days: Количество дней для статистики
            
        Returns:
            list: Список кортежей [(дата, completed), ...] 
                  где completed - 0 или 1 (выполнена или нет).
                  Возвращает пустой список если привычка не найдена
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return []

        # Преобразуем days в int (на всякий случай)
        try:
            days = int(days)
        except ValueError:
            days = 7  # значение по умолчанию

        params = (habit_id, days)
        rows = self.db.getter(self.db.GET_HABIT_STATISTIC_FOR_N_DAYS, params)

        if not rows:
            return []

        return [(row["date"], row["completed"]) for row in rows]
    
    def cleanup_old_monthly_progress(self):
        """
        Удаляет старые записи из месячной статистики.
        
        Автоматически удаляет все записи из таблицы habits_progress_monthly,
        которые старше 30 дней. Помогает поддерживать базу данных в чистоте
        и не перегружать её устаревшими данными.
        """
        self.db.execute_query_and_commit(self.db.DELETE_OLD_MONTHLY_PROGRESS)

    