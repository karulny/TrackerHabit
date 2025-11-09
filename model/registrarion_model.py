import hashlib


class AuthModel:
    """
    Модель аутентификации и управления пользователями.
    
    Управляет регистрацией, входом в систему, изменением паролей,
    темой оформления и последним временем входа пользователей.
    Все пароли хешируются с использованием SHA256.
    """

    def __init__(self, data):
        """
        Инициализация модели аутентификации.
        
        Args:
            data: Объект базы данных (DataBase)
        """
        self.db = data
        self.username = None  # Имя текущего авторизованного пользователя

    def hash_password(self, password: str):
        """
        Хеширует пароль с использованием SHA256.
        
        Args:
            password: Пароль в открытом виде
            
        Returns:
            str: Хеш пароля в шестнадцатеричном формате
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username, password):
        """
        Регистрирует нового пользователя в системе.
        
        Создает новую запись в таблице users с хешированным паролем.
        Если пользователь с таким именем уже существует, регистрация не удастся.
        
        Args:
            username: Имя пользователя (должно быть уникальным)
            password: Пароль в открытом виде (будет захеширован)
            
        Returns:
            bool: True если регистрация успешна, False при ошибке
        """
        try:
            password_hash = self.hash_password(password)
            params = (username, password_hash)
            self.db.execute_query_and_commit(self.db.INSERT_USER, params)
            return True
        except Exception as e:
            print("Не удалось зарегистрировать пользователя")
            return False

    def login_user(self, username, password):
        """
        Авторизует пользователя в системе.
        
        Проверяет соответствие хеша введенного пароля с хешем в базе данных.
        При успешной авторизации сохраняет имя пользователя в self.username.
        
        Args:
            username: Имя пользователя
            password: Пароль в открытом виде
            
        Returns:
            bool: True если авторизация успешна, False при ошибке или неверных данных
        """
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
        """
        Получает ID пользователя по его имени.
        
        Args:
            login: Имя пользователя
            
        Returns:
            int: ID пользователя из базы данных
        """
        params = (login,)
        return self.db.getter_for_one(self.db.GET_ID_ON_USERNAME, params)["id"]
    
    def update_last_login(self, user_id):
        """
        Обновляет дату последнего входа пользователя.
        
        Устанавливает поле last_login в текущую дату.
        Используется для отслеживания активности пользователя
        и определения необходимости сброса ежедневного прогресса.
        
        Args:
            user_id: ID пользователя
        """
        params = (user_id,)
        self.db.execute_query_and_commit(self.db.UPDATE_LAST_LOGIN_QUERY, params)

    def get_theme(self):
        """
        Получает текущую тему оформления пользователя.
        
        Returns:
            str или None: Название темы (например, 'dark', 'light'), 
                         или None если тема не установлена
        """
        params = (self.username,)
        theme = self.db.getter_for_one(self.db.GET_THEME_OF_USER, params)
        return theme["theme"] if theme else None
    
    def save_user_theme(self, theme_name: str):
        """
        Сохраняет выбранную тему оформления для пользователя.
        
        Args:
            theme_name: Название темы (например, 'dark', 'light')
        """
        params = (theme_name, self.username,)
        self.db.execute_query_and_commit(self.db.SET_THEME, params)

    def change_password(self, password: str):
        """
        Изменяет пароль текущего пользователя.
        
        Новый пароль хешируется и сохраняется в базе данных.
        Изменение происходит для пользователя, сохраненного в self.username.
        
        Args:
            password: Новый пароль в открытом виде (будет захеширован)
        """
        password_hash = self.hash_password(password)
        params = (password_hash, self.username)
        self.db.execute_query_and_commit(self.db.CHANGE_PASSWORD, params)