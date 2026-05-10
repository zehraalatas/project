import datetime

class Notification:
    def __init__(self, notif_id, recipient, message, is_read=False, date=None):
        self.notif_id = notif_id
        self.recipient = recipient
        self.message = message
        self.is_read = bool(is_read)
        self.date = date or datetime.date.today().isoformat()

    def mark_as_read(self):
        self.is_read = True

    def __repr__(self):
        status = "Read" if self.is_read else "Unread"
        return f"Notification(To: {self.recipient}, Status: {status}, Msg: {self.message[:20]}...)"