from models.user import User

class Patron(User):
    def __init__(self, user_id, username, off_day="Pazartesi"):
        super().__init__(user_id, username, "Patron", 0.0, None, off_day)

    def can_fire(self):
        return True

    def can_change_salary(self):
        return True

    def can_final_approve(self):
        return True

    def __repr__(self):
        return f"Patron({self.username})"