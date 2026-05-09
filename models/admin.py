from models.user import User

class Admin(User):
    def __init__(self, user_id, username, off_day="Monday", salary=0.0):
        """
        Represents the Boss (Patron) within the system.
        Inherits from User and defaults to the 'Boss' role.
        """
        super().__init__(user_id, username, "Boss", salary, None, off_day)

    def __repr__(self):
        """Professional string representation"""
        return f"Admin(Name: {self.username}, Role: {self.role})"