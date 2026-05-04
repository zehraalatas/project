class User:
    def __init__(self, user_id, username, role, salary, manager_id=None, off_day="Monday"):
        """
        Base class for all users in the Employee Management System.

        :param user_id: Unique ID from the database
        :param username: Unique login name
        :param role: System role (Boss, Manager, Waiter, etc.)
        :param salary: Monthly salary amount
        :param manager_id: ID of the assigned manager (if applicable)
        :param off_day: Assigned weekly day off (Defaults to Monday)
        """
        self.user_id = user_id
        self.username = username
        self.role = role
        self.salary = salary
        self.manager_id = manager_id
        self.off_day = off_day

    def __repr__(self):
        """String representation for basic user info"""
        return f"User({self.username}, Role: {self.role})"