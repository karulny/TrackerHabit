class MainWindowModel:
    def __init__(self, data=None):
        self.data = data

    def add_habit(self, user_id, name, category, frequency):
        """Передаем нашей БД данные и параметры их разделяем для того, чтобы не использовать f строки, которые уязвимы к
         SQL инъекции из-за этого штука выглядит сложно, но так нужно"""
        query = """
                INSERT INTO habits (user_id, name, category, frequency)
                VALUES (?, ?, ?, ?) \
                """
        params = (user_id, name, category, frequency)
        self.data.execute_query_and_commit(query, params)

    def get_habits(self, user_id):
        """Возвращает привычки и категории"""
        query = f"""SELECT * FROM habits
                WHERE user_id = ?"""
        params = (user_id,)
        return self.data.getter(query, params)

    def toggle_mark_habit(self, user_id, name):
        """Переключает отметку выполнения привычки"""
        query = """
                UPDATE habits
                SET marked = CASE WHEN marked = 1 THEN 0 ELSE 1 END
                WHERE user_id = ? \
                  AND name = ? \
                """
        params = (user_id, name)
        self.data.execute_query_and_commit(query, params)

    def close(self):
        self.data.close()

    def get_categories(self, user_id):
        """Возвращает все категории, которые существуют"""
        query = """
                SELECT DISTINCT category
                FROM habits
                WHERE user_id = ?
                """
        params = (user_id,)
        categories = self.data.getter(query, params)
        # Преобразование результата в список строк
        return [row['category'] for row in categories]

    def remove_habit(self, user_id, habit_name):
        """Удаляет привычку"""
        query = """
                DELETE
                FROM habits
                WHERE user_id = ?
                  AND name = ? \
                """
        params = (user_id, habit_name)
        return self.data.execute_query_and_commit(query, params)
