class Schedule:
    DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    def __init__(self, user_id, off_day):
        self.user_id = user_id
        self.off_day = off_day

    def get_work_days(self):
        return [d for d in self.DAYS if d != self.off_day]

    def is_working(self, day):
        return day != self.off_day

    def __repr__(self):
        return f"Schedule(user={self.user_id}, off={self.off_day})"