class ReportService:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_staff_summary(self):
        self.db.cursor.execute(
            "SELECT role, COUNT(*) FROM users WHERE role NOT IN ('Patron') GROUP BY role"
        )
        return self.db.cursor.fetchall()  # [(rol, sayı), ...]

    def get_total_salary_cost(self):
        self.db.cursor.execute(
            "SELECT SUM(salary) FROM users WHERE role NOT IN ('Patron')"
        )
        result = self.db.cursor.fetchone()[0]
        return result or 0.0

    def get_active_employee_count(self):
        self.db.cursor.execute(
            "SELECT COUNT(*) FROM users WHERE role NOT IN ('Patron')"
        )
        return self.db.cursor.fetchone()[0]