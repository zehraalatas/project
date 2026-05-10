from models.notification import Notification

class NotificationService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        self.db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                message TEXT,
                is_read INTEGER DEFAULT 0
            )
        """)
        self.db.conn.commit()

    def send(self, recipient, message):
        new_notif = Notification(None, recipient, message, is_read=0)

        query = "INSERT INTO notifications (recipient, message, is_read) VALUES (?, ?, ?)"
        self.db.cursor.execute(query, (new_notif.recipient, new_notif.message, new_notif.is_read))
        self.db.conn.commit()

    def get_unread(self, username):
        query = "SELECT id, recipient, message, is_read FROM notifications WHERE recipient=? AND is_read=0"
        self.db.cursor.execute(query, (username,))
        rows = self.db.cursor.fetchall()

        return [Notification(r[0], r[1], r[2], r[3]) for r in rows]

    def mark_all_read(self, username):
        query = "UPDATE notifications SET is_read=1 WHERE recipient=?"
        self.db.cursor.execute(query, (username,))
        self.db.conn.commit()