from models.user import User

class Employee(User):
    def __init__(self, user_id, username, role, salary, manager_id=None, off_day="Pazartesi"):
        super().__init__(user_id, username, role, salary, manager_id, off_day)

    def can_request_leave(self, role_count):
        return role_count > 1

    def get_display_name(self):
        return f"{self.role} {self.username.capitalize()}"

    def __repr__(self):
        return f"Employee({self.username}, {self.role}, {self.salary}₺)"