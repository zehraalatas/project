from models.user import User

class Patron(User):
    def __init__(self, user_id, username, off_day="Monday"):
        """
        Represents the Boss (Patron) within the system.
        Inherits from User and defaults to the 'Boss' role.
        """
        # Role updated from 'Patron' to 'Boss' for database consistency
        # Salary is set to 0.0 or could be defined as None
        super().__init__(user_id, username, "Boss", 0.0, None, off_day)

    def can_fire(self):
        """Boss has the ultimate authority to terminate contracts"""
        return True

    def can_change_salary(self):
        """Boss can manually adjust any staff member's salary"""
        return True

    def can_final_approve(self):
        """Boss gives the final 'Finalized' approval to requests"""
        return True

    def __repr__(self):
        """Professional string representation"""
        return f"Boss(Name: {self.username}, Role: {self.role})"