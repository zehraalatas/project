import datetime

class Notification:
    def __init__(self, notif_id, recipient, message, is_read=False, date=None):
        self.notif_id = notif_id
        self.recipient = recipient
        self.message = message
        self.is_read = is_read
        self.date = date or datetime.date.today().isoformat()

    def mark_as_read(self):
        self.is_read = True

    def __repr__(self):
        return f"Notification({self.recipient}: {self.message})"