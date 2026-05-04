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
        """Validates and updates user login information"""

        # Using ValidationService for business logic (Lesson Topic: Service Separation)
        if not self.validator.is_valid_username(new_username):
            return False, "Username must be at least 3 characters long!"

        if not self.validator.is_valid_password(new_password):
            return False, "Password must be at least 6 characters long!"

        # Check if the new username is already taken by someone else
        check_query = "SELECT id FROM users WHERE username=? AND id!=?"
        self.db.cursor.execute(check_query, (new_username, user_id))

        if self.db.cursor.fetchone():
            return False, "This username is already taken!"

        # Applying the update
        update_query = "UPDATE users SET username=?, password=? WHERE id=?"
        self.db.cursor.execute(update_query, (new_username, new_password, user_id))
        self.db.conn.commit()

        return True, "Credentials updated successfully!"