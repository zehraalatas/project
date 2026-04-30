from models.user import User
from services.validation_service import ValidationService
from models.user import User
from models.employee import Employee
from models.manager import Manager
from models.patron import Patron
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
            u_id, u_name, u_role, u_salary, u_mid, u_off = result

            # Rolüne göre özel sınıf nesnesi oluşturuyoruz (Polymorphism hazırlığı)
            if u_role == "Patron":
                return Patron(u_id, u_name, u_off)
            elif u_role == "Müdür":
                return Manager(u_id, u_name, u_salary, u_off)
            else:
                return Employee(u_id, u_name, u_role, u_salary, u_mid, u_off)
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