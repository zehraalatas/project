import datetime


class SalaryRecord:
    def __init__(self, record_id, user_id, old_salary, new_salary, percent, date=None):
        """
        Represents a historical record of a salary change.

        :param record_id: Unique database ID for the record
        :param user_id: ID of the employee whose salary was changed
        :param old_salary: Salary before the adjustment
        :param new_salary: Salary after the adjustment
        :param percent: The percentage of the change
        :param date: ISO format date of the record entry
        """
        self.record_id = record_id
        self.user_id = user_id
        self.old_salary = float(old_salary)
        self.new_salary = float(new_salary)
        self.percent = float(percent)
        self.date = date or datetime.date.today().isoformat()

    def get_difference(self):
        """Calculates the net change in currency"""
        return self.new_salary - self.old_salary

    def __repr__(self):
        """Professional string representation for reporting logs"""
        return f"SalaryRecord(Change: {self.old_salary:,.0f}₺ -> {self.new_salary:,.0f}₺ | {self.percent}% on {self.date})"