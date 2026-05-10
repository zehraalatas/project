from models.user import User

class Manager(User):
    def __init__(self, user_id, username, salary, off_day="Monday"):
        super().__init__(user_id, username, "Manager", salary, None, off_day)

    def __repr__(self):
        return f"Manager(Name: {self.username}, Role: {self.role})"