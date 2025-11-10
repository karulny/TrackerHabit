import hashlib


class AuthModel:
    """
    Модель аутентификации и управления пользователями.
    
    Управляет регистрацией, входом в систему, изменением паролей,
    темой оформления и последним временем входа пользователей.
    Все пароли хешируются с использованием SHA256.
    """

    def __init__(self, data):
        """Инициализация модели аутентификации"""
        self.db = data
        self.username = None  # Имя текущего авторизованного пользователя

    def hash_password(self, password: str):
        """Хеширует пароль с использованием SHA256"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username, password):
        """Регистрирует нового пользователя в системе."""
        try:
            password_hash = self.hash_password(password)
            params = (username, password_hash)
            self.db.execute_query_and_commit(self.db.INSERT_USER, params)
            return True
        except Exception as e:
            print("Не удалось зарегистрировать пользователя")
            return False

    def login_user(self, username, password):
        """Авторизует пользователя в системе."""
        password_hash = self.hash_password(password)
        try:
            params = (username,)
            password_from_bd = self.db.getter_for_one(self.db.GET_PASSWORD_ON_USERNAME, params)
            if password_from_bd and password_hash == password_from_bd["password"]:
                self.username = username
                return True
        except Exception as e:
            return False

    def get_user_id(self, login):
        """Получает ID пользователя по его имени."""
        params = (login,)
        return self.db.getter_for_one(self.db.GET_ID_ON_USERNAME, params)["id"]
    
    def update_last_login(self, user_id):
        """Обновляет дату последнего входа пользователя."""
        params = (user_id,)
        self.db.execute_query_and_commit(self.db.UPDATE_LAST_LOGIN_QUERY, params)

    def get_theme(self):
        """Получает текущую тему оформления пользователя."""
        params = (self.username,)
        theme = self.db.getter_for_one(self.db.GET_THEME_OF_USER, params)
        return theme["theme"] if theme else None
    
    def save_user_theme(self, theme_name: str):
        """Сохраняет выбранную тему оформления для пользователя."""
        params = (theme_name, self.username,)
        self.db.execute_query_and_commit(self.db.SET_THEME, params)

    def change_password(self, password: str):
        """Изменяет пароль текущего пользователя."""
        password_hash = self.hash_password(password)
        params = (password_hash, self.username)
        self.db.execute_query_and_commit(self.db.CHANGE_PASSWORD, params)