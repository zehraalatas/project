class WorkDay:
    def __init__(self, day_name, start_time="09:00", end_time="17:00", is_off=False):
        """
        Represents a single day's work configuration.

        :param day_name: Name of the day (e.g., 'Monday')
        :param start_time: Shift start (default 09:00)
        :param end_time: Shift end (default 17:00)
        :param is_off: Boolean indicating if it's the employee's day off
        """
        self.day_name = day_name
        self.start_time = start_time
        self.end_time = end_time
        self.is_off = is_off

    def get_summary(self):
        """Returns a formatted string for the UI schedule view."""
        if self.is_off:
            return f"{self.day_name}: OFF DAY"  # 'İZİNLİ' -> 'OFF DAY'
        return f"{self.day_name}: {self.start_time} - {self.end_time}"

    def __repr__(self):
        """String representation for logs"""
        status = "OFF" if self.is_off else f"{self.start_time}-{self.end_time}"
        return f"WorkDay({self.day_name}: {status})"