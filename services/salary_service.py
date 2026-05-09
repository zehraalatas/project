import datetime
from models.salary_record import SalaryRecord


class SalaryService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        """Creates the salary history table if it does not exist"""
        self.db.cursor.execute("""
                               CREATE TABLE IF NOT EXISTS salary_records
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   user_id
                                   INTEGER,
                                   old_salary
                                   REAL,
                                   new_salary
                                   REAL,
                                   percent
                                   REAL,
                                   date
                                   TEXT
                               )
                               """)
        self.db.conn.commit()

    def apply_raise(self, user_id, percentage):
        # 1. Mevcut maaşı al
        self.db.cursor.execute("SELECT salary FROM users WHERE id = ?", (user_id,))
        row = self.db.cursor.fetchone()
        if not row: return None

        current_salary = row[0]

        # 2. Yeni maaşı hesapla
        new_salary = round(current_salary * (1 + (percentage / 100)), 2)
        percentage = round(percentage, 2)

        # 3. VERİTABANINI GÜNCELLE
        self.db.cursor.execute("UPDATE users SET salary = ? WHERE id = ?", (new_salary, user_id))

        # 4. MAAŞ GEÇMİŞİNE (LOG) KAYDET
        import datetime
        today = datetime.date.today().isoformat()
        self.db.cursor.execute(
            "INSERT INTO salary_records (user_id, old_salary, new_salary, percent, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, current_salary, new_salary, percentage, today)
        )

        # 5. KAYDET
        self.db.conn.commit()

        # --- DOĞAL VE BASİT DÖNÜŞ ---
        return SalaryRecord(None, user_id, current_salary, new_salary, percentage)

    def get_history(self, user_id):
        """Retrieves all salary raise logs for a specific user"""
        query = """
                SELECT id, user_id, old_salary, new_salary, percent, date
                FROM salary_records \
                WHERE user_id=? \
                """
        self.db.cursor.execute(query, (user_id,))
        rows = self.db.cursor.fetchall()

        result = []
        for r in rows:
            record = SalaryRecord(r[0], r[1], r[2], r[3], r[4], r[5])
            result.append(record)
        return result