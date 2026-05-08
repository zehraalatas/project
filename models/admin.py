from models.user import User

class Admin(User):
    def __init__(self, user_id, username, off_day="Monday"):
        """
        Represents the Boss (Patron) within the system.
        Inherits from User and defaults to the 'Boss' role.
        """
        # Role updated from 'Patron' to 'Boss' for database consistency
        # Salary is set to 0.0 or could be defined as None
        super().__init__(user_id, username, "Boss", 0.0, None, off_day)

    def __repr__(self):
        """Professional string representation"""
        return f"Admin(Name: {self.username}, Role: {self.role})"