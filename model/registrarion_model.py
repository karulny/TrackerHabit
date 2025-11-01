import hashlib


class AuthModel:
    def __init__(self, data=None):
        self.db = data

    def hash_password(self, password: str):
        """Возвращает хэш SHA256 от пароля"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username, password):
        try:
            password_hash = self.hash_password(password)
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = (username, password_hash)
            self.db.execute_query_and_commit(query, params)
            return True
        except Exception as e:
            print("Ошибка при регистрации:", e)
            return False

    def login_user(self, username, password):
        password_hash = self.hash_password(password)
        try:
            query = "SELECT password FROM users WHERE username = ?"
            params = (username,)
            password_from_bd = self.db.getter_for_one(query, params)
            if password_from_bd and password_hash == password_from_bd[0]:
                return True
        except Exception as e:
            return False

    def get_user_id(self, login):
        query = "SELECT id FROM users WHERE username = ?"
        params = (login,)
        return self.db.getter_for_one(query, params)[0]
