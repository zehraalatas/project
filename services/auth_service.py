from models.user import User
from services.validation_service import ValidationService


class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.validator = ValidationService()

    def login(self, username, password):
        self.db.cursor.execute(
            "SELECT id, username, role, salary, manager_id, off_day FROM users WHERE username=? AND password=?",
            (username, password))
        result = self.db.cursor.fetchone()
        if result:
            return User(result[0], result[1], result[2], result[3], result[4], result[5])
        return None

    def update_credentials(self, user_id, new_username, new_password):
        # Artık ValidationService kullanıyor
        if not self.validator.is_valid_username(new_username):
            return False, "Kullanıcı adı en az 3 karakter olmalı!"

        if not self.validator.is_valid_password(new_password):
            return False, "Şifre en az 6 karakter olmalı!"

        self.db.cursor.execute("SELECT id FROM users WHERE username=? AND id!=?", (new_username, user_id))
        if self.db.cursor.fetchone():
            return False, "Bu kullanıcı adı zaten alınmış!"

        self.db.cursor.execute("UPDATE users SET username=?, password=? WHERE id=?",
                               (new_username, new_password, user_id))
        self.db.conn.commit()
        return True, "Bilgiler başarıyla güncellendi!"