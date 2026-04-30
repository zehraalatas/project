from models.notification import Notification  # Sınıfı içeri al


class NotificationService:
    def __init__(self, db_manager):
        self.db = db_manager

    def send(self, recipient, message):
        # 1. Önce Nesneyi Oluştur (OOP Mantığı)
        # ID'yi veritabanı vereceği için 0 veya None geçebiliriz
        new_notif = Notification(None, recipient, message, is_read=0)

        # 2. Nesne üzerinden veritabanına kaydet
        self.db.cursor.execute(
            "INSERT INTO notifications (recipient, message, is_read) VALUES (?, ?, ?)",
            (new_notif.recipient, new_notif.message, new_notif.is_read)
        )
        self.db.conn.commit()

    def get_unread(self, username):
        self.db.cursor.execute(
            "SELECT id, recipient, message, is_read FROM notifications WHERE recipient=? AND is_read=0",
            (username,)
        )
        rows = self.db.cursor.fetchall()

        # 3. Veritabanından gelen ham veriyi (tuple) Notification nesnelerine dönüştür (Mapping)
        return [Notification(r[0], r[1], r[2], r[3]) for r in rows]

    def mark_all_read(self, username):
        # Burada nesne üzerinden tek tek güncelleme de yapabiliriz ama performans için toplu güncelliyoruz
        self.db.cursor.execute(
            "UPDATE notifications SET is_read=1 WHERE recipient=?",
            (username,)
        )
        self.db.conn.commit()