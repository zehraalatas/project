from models.work_day import WorkDay

class Schedule:
    def __init__(self, user_id, off_day_name):
        self.user_id = user_id
        self.DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        self.weekly_plan = []
        for d in self.DAYS:
            is_off = (d == off_day_name)
            self.weekly_plan.append(WorkDay(d, is_off=is_off))

    def __repr__(self):
        return f"Schedule(UserID: {self.user_id}, Days: {len(self.weekly_plan)})"