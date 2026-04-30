class WorkDay:
    def __init__(self, day_name, start_time="09:00", end_time="18:00", is_off=False):
        self.day_name = day_name
        self.start_time = start_time
        self.end_time = end_time
        self.is_off = is_off

    def get_summary(self):
        if self.is_off:
            return f"{self.day_name}: İZİNLİ"
        return f"{self.day_name}: {self.start_time} - {self.end_time}"