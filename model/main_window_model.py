from datetime import date, datetime


class MainWindowModel:
    # Константы запросов
    INSERT_HABIT_QUERY = """
                         INSERT INTO habits (user_id, name, category, daily_frequency)
                         VALUES (?, ?, ?, ?) \
                         """

    SELECT_HABITS_QUERY = """
                          SELECT *
                          FROM habits
                          WHERE user_id = ? \
                          """

    UPDATE_HABIT_MARK_QUERY = """
                              UPDATE habit_progress
                              SET progress = progress + 1
                              WHERE habit_id = ? \
                              """

    SELECT_CATEGORIES_QUERY = """
                              SELECT DISTINCT category
                              FROM habits
                              WHERE user_id = ? \
                              """

    RESET_DAILY_PROGRESS = """DELETE
                              FROM habit_progress
                              WHERE date(date) < date('now'); \
                           """

    ADD_HABIT_PROGRESS = """
                         INSERT INTO habit_progress (habit_id, date, progress, target)
                         VALUES (?, date('now'), ?, ?) \
                         """

    ADD_MONTHLY_PROGRESS = """
                           INSERT INTO habits_progress_monthly (habit_id, date, completed)
                           VALUES (?, date('now'), ?) \
                           """
    GET_LAST_HABIT_PROGRESS_AND_TARGET = """
                                         SELECT progress, target
                                         FROM habit_progress
                                         WHERE habit_id = ?
                                           AND date = date('now', 'localtime') -- Важное уточнение
                                         ORDER BY date DESC
                                         LIMIT 1 \
                                         """

    UPDATE_LAST_HABIT_PROGRESS = """
                                 UPDATE habits_progress_monthly
                                 SET date      = date('now'),
                                     completed = ?
                                 WHERE habit_id = ? \
                                 """

    IS_HABIT_COMPLETED_TODAY = """
                               SELECT progress, target
                               FROM habit_progress
                               WHERE habit_id = ? \
                               """

    DELETE_HABIT_PROGRESS = """
                            DELETE
                            FROM habit_progress
                            WHERE habit_id = ? \
                            """

    DELETE_HABIT_PROGRESS_MONTHLY_QUERY = """
                                          DELETE
                                          FROM habits_progress_monthly
                                          WHERE habit_id = ?; \
                                          """

    DELETE_HABIT_QUERY = """
                         DELETE
                         FROM habits
                         WHERE user_id = ?
                           AND name = ?; \
                         """

    GET_HABIT_ID_QUERY = """
                         SELECT id
                         FROM habits
                         WHERE user_id = ?
                           AND name = ? \
                         """

    GET_LAST_DATE_QUERY = """
                          SELECT last_login AS date
                          FROM users
                          WHERE id = ?
                          ORDER BY date DESC
                          LIMIT 1 \
                          """

    GET_DAILY_PROGRESS_TARGET = """
                                SELECT progress, target, date
                                FROM habit_progress \
                                WHERE habit_id = ?
                                """

    GET_MONTHLY_PROGRESS = """
                           SELECT completed, date
                           FROM habits_progress_monthly
                           WHERE id = ? \
                           """

    def __init__(self, data, user_id):
        self.db = data
        self.user_id = user_id
        if self.today_is_new_day():
            self.reset_daily_progress()

        if self.month_is_new():
            self.reset_monthly_progress()

    def add_habit(self, name, category, frequency):
        """Передаем нашей БД данные и параметры их разделяем для того, чтобы не использовать f строки, которые уязвимы к
         SQL инъекции из-за этого штука выглядит сложно, но так нужно"""
        params = (self.user_id, name, category, frequency)
        self.db.execute_query_and_commit(self.INSERT_HABIT_QUERY, params)
        habit_id = self.get_habit_id(name)
        # Инициализируем прогресс для новой привычки
        progress_params = (habit_id, 0, frequency)
        self.db.execute_query_and_commit(self.ADD_HABIT_PROGRESS, progress_params)
        monthly_params = (habit_id, 0)
        self.db.execute_query_and_commit(self.ADD_MONTHLY_PROGRESS, monthly_params)

    def get_habits(self):
        """Возвращает привычки и категории"""
        params = (self.user_id,)
        return self.db.getter(self.SELECT_HABITS_QUERY, params)

    def toggle_mark_habit(self, habit_name):
        """Переключает отметку выполнения привычки"""
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        self.db.execute_query_and_commit(self.UPDATE_HABIT_MARK_QUERY, params)
        completed = self.is_habit_completed_today(habit_name)
        if completed:
            self.db.execute_query_and_commit(self.UPDATE_LAST_HABIT_PROGRESS, (1, habit_id))

    def get_progress_and_target(self, habit_name):
        """Возвращает прогресс и цель по названию привычки"""
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        row = self.db.getter_for_one(self.GET_LAST_HABIT_PROGRESS_AND_TARGET, params)
        if row:
            return row['progress'], row['target']
        return 0, 0  # Если нет записи, возвращаем 0 прогресс и 0 цель

    def close(self):
        self.db.close()

    def get_categories(self):
        """Возвращает все категории, которые существуют"""
        params = (self.user_id,)
        categories = self.db.getter(self.SELECT_CATEGORIES_QUERY, params)
        # Преобразование результата в список строк
        return [row['category'] for row in categories]

    def remove_habit(self, habit_name):
        """Удаляет привычку"""
        habit_id = self.get_habit_id(habit_name)
        params = (self.user_id, habit_name)
        self.db.execute_query_and_commit(self.DELETE_HABIT_PROGRESS, (habit_id,))
        self.db.execute_query_and_commit(self.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, (habit_id,))
        self.db.execute_query_and_commit(self.DELETE_HABIT_QUERY, params)

    def is_habit_completed_today(self, habit_name):
        """Проверяет, выполнена ли привычка сегодня"""
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        row = self.db.getter_for_one(self.IS_HABIT_COMPLETED_TODAY, params)

        if row['progress'] >= row['target'] and row:
            return True
        return False

    def reset_daily_progress(self):
        """Сбрасывает ежедневный прогресс для всех привычек"""
        self.db.execute_query_and_commit(self.RESET_DAILY_PROGRESS)
        self.init_new_progress_for_habits()

    def get_habit_id(self, habit_name):
        """Получает ID привычки по её названию"""
        params = (self.user_id, habit_name)
        row = self.db.getter_for_one(self.GET_HABIT_ID_QUERY, params)
        return row['id'] if row else None

    def today_is_new_day(self):
        """Проверяет, является ли сегодня новым днём для сброса прогресса"""
        today = date.today().isoformat()
        params = (self.user_id,)
        row = self.db.getter_for_one(self.GET_LAST_DATE_QUERY, params)
        if row and row['date'] < today:
            return True
        return False

    def init_new_progress_for_habits(self):
        """Инициализирует новый прогресс для привычки в начале нового дня"""
        habits_id_and_frequency = [(self.get_habit_id(habit["name"]), habit["daily_frequency"]) for habit in
                                   self.get_habits()]
        for habit_id, frequency in habits_id_and_frequency:
            params = (habit_id, 0, frequency)
            self.db.execute_query_and_commit(self.ADD_HABIT_PROGRESS, params)
            self.db.execute_query_and_commit(self.ADD_MONTHLY_PROGRESS, (habit_id, 0))

    def month_is_new(self):
        """Проверяет, наступил ли новый месяц с последнего входа пользователя"""
        params = (self.user_id,)
        row = self.db.getter_for_one(self.GET_LAST_DATE_QUERY, params)
        if not row:
            return False

        last_date = datetime.strptime(row['date'], "%Y-%m-%d").date()
        today = datetime.today().date()

        # Проверяем, другой ли это месяц
        if last_date.month != today.month or last_date.year != today.year:
            return True
        return False

    def reset_monthly_progress(self):
        """Сбрасывает ежемесячный прогресс всех привычек"""
        # Удаляем записи старого месяца
        self.db.execute_query_and_commit("DELETE FROM habits_progress_monthly;")

        # Создаём новые записи для текущего месяца
        habits_id = [self.get_habit_id(habit["name"]) for habit in self.get_habits()]
        for habit_id in habits_id:
            self.db.execute_query_and_commit(
                "INSERT INTO habits_progress_monthly (habit_id, date, completed) VALUES (?, date('now'), 0);",
                (habit_id,)
            )

        # Обновляем дату последнего входа, чтобы не сбрасывать повторно
        self.db.execute_query_and_commit(
            "UPDATE users SET last_login = date('now') WHERE id = ?;", (self.user_id,)
        )

    def get_habit_static_daily(self, habit_name):
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        res = self.db.getter(self.GET_DAILY_PROGRESS_TARGET, params)
        if res:
            return [(res['progress'], res['target'], res['date']) for res in res]
        return 0, 0, 0

    def get_habit_static_monthly(self, habit_name):
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        res = self.db.getter(self.GET_MONTHLY_PROGRESS, params)
        if res:
            return [(res['progress'], res['target'], datetime.strptime(res['date'], "%Y-%m-%d")) for res in res]
        return 0, 0, 0
