import datetime

class SalaryRecord:
    def __init__(self, record_id, user_id, old_salary, new_salary, percent, date=None):
        self.record_id = record_id
        self.user_id = user_id
        self.old_salary = old_salary
        self.new_salary = new_salary
        self.percent = percent
        self.date = date or datetime.date.today().isoformat()

    def difference(self):
        return self.new_salary - self.old_salary

    def __repr__(self):
        return f"SalaryRecord({self.old_salary}₺ → {self.new_salary}₺, %{self.percent})"