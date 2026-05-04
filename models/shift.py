import datetime


class Shift:
    def __init__(self, shift_id, user_id, username, date, status, hours=8):
        """
        Represents a single work shift record for an employee.

        :param shift_id: Unique database ID for the shift entry
        :param user_id: ID of the employee
        :param username: Display name of the employee
        :param date: The date of the shift (ISO format)
        :param status: Work status (e.g., 'Working', 'Off', 'Sick Leave')
        :param hours: Total hours worked during this shift
        """
        self.shift_id = shift_id
        self.user_id = user_id
        self.username = username
        self.date = date
        self.status = status  # Now using English status: 'Working' or 'Off'
        self.hours = hours

    def __repr__(self):
        """Professional string representation for shift logs"""
        return f"Shift(User: {self.username}, Date: {self.date}, Duration: {self.hours} hrs)"