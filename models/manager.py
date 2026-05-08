from models.user import User

class Manager(User):
    def __init__(self, user_id, username, salary, off_day="Monday"):
        """
        Represents a Manager within the system.
        Inherits from User and defaults to the 'Manager' role.
        """
        # Role updated from 'Müdür' to 'Manager'
        super().__init__(user_id, username, "Manager", salary, None, off_day)

    def __repr__(self):
        """Professional string representation"""
        return f"Manager(Name: {self.username}, Role: {self.role})"