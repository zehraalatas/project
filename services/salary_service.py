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
        new_salary = current_salary * (1 + (percentage / 100))

        # 3. VERİTABANINI GÜNCELLE (En kritik yer)
        self.db.cursor.execute("UPDATE users SET salary = ? WHERE id = ?", (new_salary, user_id))

        # 4. KAYDET (Bu olmazsa maaş değişmez!)
        self.db.connection.commit()

        # Geriye bir nesne döndür (Dashboard'un anlaması için)
        from dataclasses import make_dataclass
        Result = make_dataclass("Result", [("new_salary", float)])
        return Result(new_salary=new_salary)

    def get_history(self, user_id):
        """Retrieves all salary raise logs for a specific user"""
        query = """
                SELECT id, user_id, old_salary, new_salary, percent, date
                FROM salary_records \
                WHERE user_id=? \
                """
        self.db.cursor.execute(query, (user_id,))
        rows = self.db.cursor.fetchall()

        # Convert raw tuples into SalaryRecord objects (Lesson Topic: Mapping)
        return [SalaryRecord(*r) for r in rows]