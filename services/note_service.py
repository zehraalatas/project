import datetime
from models.note import Note

class NoteService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        query = "INSERT INTO notes (sender_name, sender_role, target_role, content, date) VALUES (?, ?, ?, ?, ?)"

        self.db.cursor.execute(query, (sender_name, sender_role, target_role, content, current_time))
        self.db.conn.commit()

    def get_notes_for_user(self, user_role):
        if user_role in ['Manager', 'Boss']:
            self.db.cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        else:
            self.db.cursor.execute("SELECT * FROM notes WHERE target_role=? ORDER BY id DESC", (user_role,))

        rows = self.db.cursor.fetchall()
        return [Note(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]