from models.employee import Employee
from models.manager import Manager
from models.admin import Admin

class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager

    def login(self, username, password):
        query = "SELECT id, username, role, salary, manager_id, off_day FROM users WHERE username=? AND password=?"
        self.db.cursor.execute(query, (username, password))
        result = self.db.cursor.fetchone()

        if result:
            u_id, u_name, u_role, u_salary, u_mid, u_off = result

            if u_role == "Boss":
                return Admin(u_id, u_name, u_off, u_salary)
            elif u_role == "Manager":
                return Manager(u_id, u_name, u_salary, u_off)
            else:
                return Employee(u_id, u_name, u_role, u_salary, u_mid, u_off)

        return None

    def update_credentials(self, user_id, new_username, new_password):

        self.db.cursor.execute(
            "SELECT id FROM users WHERE username=? AND id!=?",
            (new_username, user_id)
        )

        if self.db.cursor.fetchone():
            return False, "⚠️ This username is already taken!"

        try:
            self.db.cursor.execute(
                "UPDATE users SET username=?, password=? WHERE id=?",
                (new_username, new_password, user_id)
            )
            self.db.conn.commit()
            return True, "✅ Credentials updated successfully!"
        except Exception as e:
            return False, f"Error: {e}"