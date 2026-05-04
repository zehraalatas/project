class ReportService:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_staff_summary(self):
        """Returns a summary of staff counts grouped by their roles"""
        # CRITICAL: Filter updated from 'Patron' to 'Boss'
        query = """
                SELECT role, COUNT(*)
                FROM users
                WHERE role != 'Boss'
                GROUP BY role \
                """
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()  # Returns list of tuples: [(role, count), ...]

    def get_total_salary_cost(self):
        """Calculates the total monthly salary expense for all employees"""
        query = "SELECT SUM(salary) FROM users WHERE role != 'Boss'"
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchone()[0]

        # Returning 0.0 if there are no employees to prevent NoneType errors
        return result or 0.0

    def get_active_employee_count(self):
        """Returns the total number of active staff members (excluding the Boss)"""
        query = "SELECT COUNT(*) FROM users WHERE role != 'Boss'"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchone()[0]