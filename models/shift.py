import datetime

class Shift:
    def __init__(self, shift_id, user_id, username, date=None, hours=8):
        self.shift_id = shift_id
        self.user_id = user_id
        self.username = username
        self.date = date or datetime.date.today().isoformat()
        self.hours = hours

    def __repr__(self):
        return f"Shift({self.username}, {self.date}, {self.hours}sa)"