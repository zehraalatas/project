class User:
    def __init__(self, user_id, username, role, salary, manager_id=None, off_day="Monday"):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.salary = salary
        self.manager_id = manager_id
        self.off_day = off_day

    def __repr__(self):
        return f"User({self.username}, Role: {self.role})"