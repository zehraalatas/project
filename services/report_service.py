class ReportService:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_staff_summary(self):
        query = """
                SELECT role, COUNT(*)
                FROM users
                WHERE role != 'Boss'
                GROUP BY role \
                """
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def get_total_salary_cost(self):
        query = "SELECT SUM(salary) FROM users WHERE role != 'Boss'"
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchone()[0]

        return result or 0.0

    def get_active_employee_count(self):
        query = "SELECT COUNT(*) FROM users WHERE role != 'Boss'"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchone()[0]