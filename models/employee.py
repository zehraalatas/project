from models.user import User

class Employee(User):
    def __init__(self, user_id, username, role, salary, manager_id=None, off_day="Monday"):
        """
        Represents a standard staff member (Waiter, Chef, Barista, etc.)
        Inherits core identity from the User class.
        """
        super().__init__(user_id, username, role, salary, manager_id, off_day)

    def can_request_leave(self, role_count):
        """
        Business Logic: Staff can only request leave if there's someone
        else working in the same role to cover the shift.
        """
        return role_count > 1

    def get_display_name(self):
        """Returns a formatted name for UI display"""
        return f"{self.role} {self.username.capitalize()}"

    def __repr__(self):
        """Professional string representation for debugging"""
        return f"Employee(Name: {self.username}, Role: {self.role}, Salary: {self.salary}₺)"