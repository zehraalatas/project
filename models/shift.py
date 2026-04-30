import datetime

class Shift:
    def __init__(self, shift_id, user_id, username, date, status):
        self.shift_id = shift_id
        self.user_id = user_id
        self.username = username
        self.date = date
        self.status = status # Hatanın çözümü tam olarak buradaki isim!

    def __repr__(self):
        return f"Shift({self.username}, {self.date}, {self.hours}sa)"