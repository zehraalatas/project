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
                is_read INTEGER DEFAULT 0,
                date TEXT
            )
        """)
        self.db.conn.commit()

    def send(self, recipient, message):
        import datetime
        date = datetime.date.today().isoformat()
        self.db.cursor.execute(
            "INSERT INTO notifications (recipient, message, is_read, date) VALUES (?, ?, 0, ?)",
            (recipient, message, date)
        )
        self.db.conn.commit()

    def get_unread(self, recipient):
        self.db.cursor.execute(
            "SELECT id, recipient, message, is_read, date FROM notifications WHERE recipient=? AND is_read=0",
            (recipient,)
        )
        rows = self.db.cursor.fetchall()
        return [Notification(r[0], r[1], r[2], bool(r[3]), r[4]) for r in rows]

    def mark_all_read(self, recipient):
        self.db.cursor.execute(
            "UPDATE notifications SET is_read=1 WHERE recipient=?", (recipient,)
        )
        self.db.conn.commit()