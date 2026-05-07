from models.user import User
from models.employee import Employee
from models.manager import Manager
from models.patron import Patron  # This corresponds to the Boss class
from services.validation_service import ValidationService


class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.validator = ValidationService()

    def login(self, username, password):
        """Authenticates the user and returns a role-specific object"""
        query = "SELECT id, username, role, salary, manager_id, off_day FROM users WHERE username=? AND password=?"
        self.db.cursor.execute(query, (username, password))
        result = self.db.cursor.fetchone()

        if result:
            u_id, u_name, u_role, u_salary, u_mid, u_off = result

            # Creating specific objects based on roles (Polymorphism)
            # Updated to match our new English database values
            if u_role == "Boss":
                return Patron(u_id, u_name, u_off)
            elif u_role == "Manager":
                return Manager(u_id, u_name, u_salary, u_off)
            else:
                # Default for Waiter, Chef, etc.
                return Employee(u_id, u_name, u_role, u_salary, u_mid, u_off)

        return None

    def update_credentials(self, user_id, new_username, new_password):
        """Kullanıcı adı ve şifreyi günceller, isim çakışmasını engeller."""

        # 1. İSİM ÇAKIŞMASI KONTROLÜ
        # Veritabanında bu 'new_username'e sahip BAŞKA BİRİ (id != user_id) var mı?
        self.db.cursor.execute(
            "SELECT id FROM users WHERE username=? AND id!=?",
            (new_username, user_id)
        )

        if self.db.cursor.fetchone():
            # Eğer kayıt dönerse, bu isim başkası tarafından kullanılıyor demektir.
            return False, "⚠️ This username is already taken!"

        # 2. GÜNCELLEME İŞLEMİ (Eğer isim boşta ise)
        try:
            self.db.cursor.execute(
                "UPDATE users SET username=?, password=? WHERE id=?",
                (new_username, new_password, user_id)
            )
            self.db.conn.commit()
            return True, "✅ Credentials updated successfully!"
        except Exception as e:
            return False, f"Database error: {e}"