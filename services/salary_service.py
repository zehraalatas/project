from models.salary_record import SalaryRecord

class SalaryService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        self.db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                old_salary REAL,
                new_salary REAL,
                percent REAL,
                date TEXT
            )
        """)
        self.db.conn.commit()

    def apply_raise(self, user_id, percent):
        self.db.cursor.execute("SELECT salary FROM users WHERE id=?", (user_id,))
        result = self.db.cursor.fetchone()
        if not result:
            return None

        old_salary = result[0]
        new_salary = round(old_salary * (1 + percent / 100))

        self.db.cursor.execute("UPDATE users SET salary=? WHERE id=?", (new_salary, user_id))

        import datetime
        date = datetime.date.today().isoformat()
        self.db.cursor.execute(
            "INSERT INTO salary_records (user_id, old_salary, new_salary, percent, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, old_salary, new_salary, percent, date)
        )
        self.db.conn.commit()

        return SalaryRecord(None, user_id, old_salary, new_salary, percent, date)

    def get_history(self, user_id):
        self.db.cursor.execute(
            "SELECT id, user_id, old_salary, new_salary, percent, date FROM salary_records WHERE user_id=?",
            (user_id,)
        )
        rows = self.db.cursor.fetchall()
        return [SalaryRecord(*r) for r in rows]