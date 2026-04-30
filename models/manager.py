from models.user import User

class Manager(User):
    def __init__(self, user_id, username, salary, off_day="Pazartesi"):
        super().__init__(user_id, username, "Müdür", salary, None, off_day)

    def can_approve_requests(self):
        return True

    def can_hire(self):
        return True

    def __repr__(self):
        return f"Manager({self.username})"