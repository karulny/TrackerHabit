from datetime import date, datetime


class MainWindowModel:
    # Константы запросов
    # Добавляем новую запись в habit_progress с текущим временем
    ADD_HABIT_PROGRESS = """
                         INSERT INTO habit_progress (habit_id, date, progress, target)
                         VALUES (?, datetime('now', 'localtime'), ?, ?); \
                         """

    # Получаем последнюю запись за сегодня
    GET_LAST_TODAY_PROGRESS = """
                              SELECT progress, target
                              FROM habit_progress
                              WHERE habit_id = ?
                                AND date(date) = date('now', 'localtime') -- фильтруем только по сегодняшней дате
                              ORDER BY id DESC
                              LIMIT 1; \
                              """

    # Проверка в monthly (можно оставить только по дате)
    CHECK_IF_TODAY_MONTHLY_EXISTS = """
                                    SELECT id
                                    FROM habits_progress_monthly
                                    WHERE habit_id = ?
                                      AND date = date('now', 'localtime'); \
                                    """

    # Получить цель прогресс
    GET_LAST_HABIT_PROGRESS_AND_TARGET = """
                                         SELECT progress, target
                                         FROM habit_progress
                                         WHERE habit_id = ?
                                           AND date = date('now', 'localtime')
                                         ORDER BY id DESC
                                         LIMIT 1; \
                                         """

    # Добавляем запись в habits_progress_monthly
    ADD_MONTHLY_PROGRESS = """
                           INSERT INTO habits_progress_monthly (habit_id, date, completed)
                           VALUES (?, date('now', 'localtime'), ?); \
                           """

    # Обновляем запись в habits_progress_monthly
    UPDATE_LAST_HABIT_PROGRESS = """
                                 UPDATE habits_progress_monthly
                                 SET completed = ?
                                 WHERE habit_id = ?
                                   AND date = datetime('now', 'localtime'); \
                                 """

    # Получить daily_frequency (target)
    GET_HABIT_TARGET = """
                       SELECT daily_frequency
                       FROM habits
                       WHERE id = ?; \
                       """

    INSERT_HABIT_QUERY = """
                         INSERT INTO habits (user_id, name, category, daily_frequency)
                         VALUES (?, ?, ?, ?) \
                         """

    SELECT_HABITS_QUERY = """
                          SELECT *
                          FROM habits
                          WHERE user_id = ? \
                          """

    SELECT_CATEGORIES_QUERY = """
                              SELECT DISTINCT category
                              FROM habits
                              WHERE user_id = ? \
                              """

    RESET_DAILY_PROGRESS = """DELETE
                              FROM habit_progress
                              WHERE date(date) < date('now', 'localtime'); \
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
                               ORDER BY id DESC
                               LIMIT 1 \
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

    DELETE_HABITS = "DELETE  FROM habits WHERE user_id = ?"

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

    GET_DAILY_PROGRESS = """
                         SELECT date
                         FROM habit_progress \
                         WHERE habit_id = ? \
                         """

    GET_HABIT_STATISTIC_FOR_N_DAYS = """
                                     SELECT completed, date
                                     FROM habits_progress_monthly
                                     WHERE habit_id = ?
                                       AND date >= date('now', '-' || ? || ' days')
                                     ORDER BY date ASC; \
                                     """

    DELETE_OLD_MONTHLY_PROGRESS = """
                                  DELETE
                                  FROM habits_progress_monthly
                                  WHERE date < date('now', '-30 days'); \
                                  """

    def __init__(self, data, user_id):
        self.db = data
        self.user_id = user_id
        if self.today_is_new_day():
            print("да")
            self.reset_daily_progress()
        self.cleanup_old_monthly_progress()

    def add_habit(self, name, category, frequency):
        params = (self.user_id, name, category, frequency)
        self.db.execute_query_and_commit(self.INSERT_HABIT_QUERY, params)
        habit_id = self.get_habit_id(name)

        # Добавляем запись в monthly, только если её нет
        exists = self.db.getter_for_one(self.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
        if not exists:
            monthly_params = (habit_id, 0)
            self.db.execute_query_and_commit(self.ADD_MONTHLY_PROGRESS, monthly_params)

    def get_habits(self):
        """Возвращает привычки и категории"""
        params = (self.user_id,)
        return self.db.getter(self.SELECT_HABITS_QUERY, params)

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
        last_row = self.db.getter_for_one(self.GET_LAST_TODAY_PROGRESS, (habit_id,))

        # Получаем целевой daily_frequency
        target_row = self.db.getter_for_one(self.GET_HABIT_TARGET, (habit_id,))
        target = target_row["daily_frequency"] if target_row else 1

        if last_row:
            new_progress = last_row["progress"] + 1
        else:
            new_progress = 1  # если сегодня нет записей, начинаем с 1

        # Добавляем новую строку с текущим временем
        params = (habit_id, new_progress, target)
        self.db.execute_query_and_commit(self.ADD_HABIT_PROGRESS, params)

        # Если достигнута цель — обновляем/добавляем запись в monthly
        if new_progress >= target:
            exists = self.db.getter_for_one(self.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
            if exists:
                self.db.execute_query_and_commit(self.UPDATE_LAST_HABIT_PROGRESS, (1, habit_id))
            else:
                self.db.execute_query_and_commit(self.ADD_MONTHLY_PROGRESS, (habit_id, 1))

    def get_progress_and_target(self, habit_name):
        """
        Возвращает (progress, target) последней записи за сегодня.
        Если записей за сегодня нет — возвращает (0, daily_frequency).
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return 0, 0

        row = self.db.getter_for_one(self.GET_LAST_TODAY_PROGRESS, (habit_id,))
        if row:
            return row["progress"], row["target"]

        # Если записей нет — возвращаем 0 и target из таблицы habits
        tgt_row = self.db.getter_for_one(self.GET_HABIT_TARGET, (habit_id,))
        target = tgt_row['daily_frequency'] if tgt_row else 1
        return 0, target

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
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return False

        row = self.db.getter_for_one(self.GET_LAST_TODAY_PROGRESS, (habit_id,))
        # если есть последняя запись — сравниваем её progress с target
        if row:
            return row.get('progress', 0) >= row.get('target', 0)

        # если записей нет — совпадения нет
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
        print(date.today().isoformat())
        today = date.today().isoformat()
        params = (self.user_id,)
        row = self.db.getter_for_one(self.GET_LAST_DATE_QUERY, params)
        print(row['date'])
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
            # Проверяем, есть ли уже запись за сегодня в habit_progress
            self.db.execute_query_and_commit(self.ADD_HABIT_PROGRESS, (habit_id, 0, frequency))

            # Проверяем, есть ли запись в monthly за сегодня
            exists = self.db.getter_for_one(self.CHECK_IF_TODAY_MONTHLY_EXISTS, (habit_id,))
            if not exists:
                # Добавляем только если нет
                self.db.execute_query_and_commit(self.ADD_MONTHLY_PROGRESS, (habit_id, 0))

    def get_habit_static_daily(self, habit_name):
        habit_id = self.get_habit_id(habit_name)
        params = (habit_id,)
        rows = self.db.getter(self.GET_DAILY_PROGRESS, params)
        if rows:
            result = [(row['date'], 1) for row in rows]
            return result
        return

    def reset_data(self):
        params = (self.user_id,)
        self.db.execute_query_and_commit(self.DELETE_HABITS, params)
        self.db.execute_query_and_commit(self.DELETE_HABIT_PROGRESS, params)
        self.db.execute_query_and_commit(self.DELETE_HABIT_PROGRESS_MONTHLY_QUERY, params)

    def get_habit_static_for_N_days(self, habit_name, days):
        """
        Возвращает [(дата, выполнено)] за последние N дней
        """
        habit_id = self.get_habit_id(habit_name)
        if not habit_id:
            return []

        # Преобразуем days в int (на всякий случай, если пришёл текст)
        try:
            days = int(days)
        except ValueError:
            days = 7  # значение по умолчанию

        params = (habit_id, days)
        rows = self.db.getter(self.GET_HABIT_STATISTIC_FOR_N_DAYS, params)

        if not rows:
            return []

        return [(row["date"], row["completed"]) for row in rows]

    def cleanup_old_monthly_progress(self):
        """Удаляет записи старше 30 дней из таблицы habits_progress_monthly"""
        self.db.execute_query_and_commit(self.DELETE_OLD_MONTHLY_PROGRESS)
