from models.note import Note


class NoteService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        # Eğer notes tablosu yoksa otomatik oluşturur (Böylece db_manager'ı ellemene gerek kalmaz)
        self.db.cursor.execute("""
                               CREATE TABLE IF NOT EXISTS notes
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   sender_name
                                   TEXT,
                                   sender_role
                                   TEXT,
                                   target_role
                                   TEXT,
                                   content
                                   TEXT,
                                   date
                                   TEXT
                               )
                               """)
        self.db.conn.commit()

    def add_note(self, sender_name, sender_role, target_role, content):
        import datetime
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.cursor.execute(
            "INSERT INTO notes (sender_name, sender_role, target_role, content, date) VALUES (?, ?, ?, ?, ?)",
            (sender_name, sender_role, target_role, content, date)
        )
        self.db.conn.commit()

    def get_notes_for_user(self, user_role):
        # Müdür ve Patron tüm notları görür, çalışanlar sadece kendi rolüne atılanları görür
        if user_role in ['Müdür', 'Patron']:
            self.db.cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        else:
            self.db.cursor.execute("SELECT * FROM notes WHERE target_role=? ORDER BY id DESC", (user_role,))

        rows = self.db.cursor.fetchall()
        # Ham veriyi Note nesnelerine dönüştürüp liste olarak dönüyoruz
        return [Note(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]