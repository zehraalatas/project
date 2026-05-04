import datetime


class Notification:
    def __init__(self, notif_id, recipient, message, is_read=False, date=None):
        """
        Represents a personal notification for a specific user.

        :param notif_id: Unique database ID for the notification
        :param recipient: Username of the person receiving the message
        :param message: The content of the notification (e.g., 'Your leave was approved!')
        :param is_read: Boolean flag to track if the user has seen the message
        :param date: ISO format date of when the notification was generated
        """
        self.notif_id = notif_id
        self.recipient = recipient
        self.message = message
        self.is_read = bool(is_read)  # Ensures boolean type from DB (0 or 1)
        self.date = date or datetime.date.today().isoformat()

    def mark_as_read(self):
        """Logic to flag the notification as seen by the user"""
        self.is_read = True

    def __repr__(self):
        """Professional string representation for debugging notification logs"""
        status = "Read" if self.is_read else "Unread"
        return f"Notification(To: {self.recipient}, Status: {status}, Msg: {self.message[:20]}...)"