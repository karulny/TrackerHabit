class MainWindowModel:
    # Константы запросов
    INSERT_HABIT_QUERY = """
                         INSERT INTO habits (user_id, name, category, frequency)
                         VALUES (?, ?, ?, ?) \
                         """

    SELECT_HABITS_QUERY = """
                          SELECT * \
                          FROM habits
                          WHERE user_id = ? \
                          """

    UPDATE_HABIT_MARK_QUERY = """
                              UPDATE habits
                              SET marked = CASE WHEN marked = 1 THEN 0 ELSE 1 END
                              WHERE user_id = ?
                                AND name = ? \
                              """

    SELECT_CATEGORIES_QUERY = """
                              SELECT DISTINCT category
                              FROM habits
                              WHERE user_id = ? \
                              """

    DELETE_HABIT_QUERY = """
                         DELETE
                         FROM habits
                         WHERE user_id = ?
                           AND name = ? \
                         """

    def __init__(self, data=None):
        self.data = data

    def add_habit(self, user_id, name, category, frequency):
        """Передаем нашей БД данные и параметры их разделяем для того, чтобы не использовать f строки, которые уязвимы к
         SQL инъекции из-за этого штука выглядит сложно, но так нужно"""
        params = (user_id, name, category, frequency)
        self.data.execute_query_and_commit(self.INSERT_HABIT_QUERY, params)

    def get_habits(self, user_id):
        """Возвращает привычки и категории"""
        params = (user_id,)
        return self.data.getter(self.SELECT_HABITS_QUERY, params)

    def toggle_mark_habit(self, user_id, name):
        """Переключает отметку выполнения привычки"""
        params = (user_id, name)
        self.data.execute_query_and_commit(self.UPDATE_HABIT_MARK_QUERY, params)

    def close(self):
        self.data.close()

    def get_categories(self, user_id):
        """Возвращает все категории, которые существуют"""
        params = (user_id,)
        categories = self.data.getter(self.SELECT_CATEGORIES_QUERY, params)
        # Преобразование результата в список строк
        return [row['category'] for row in categories]

    def remove_habit(self, user_id, habit_name):
        """Удаляет привычку"""
        params = (user_id, habit_name)
        return self.data.execute_query_and_commit(self.DELETE_HABIT_QUERY, params)