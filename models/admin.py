from models.user import User

class Admin(User):
    def __init__(self, user_id, username, off_day="Monday", salary=0.0):
        super().__init__(user_id, username, "Boss", salary, None, off_day)

    def __repr__(self):
        return f"Admin(Name: {self.username}, Role: {self.role})"