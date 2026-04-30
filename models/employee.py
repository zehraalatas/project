class WorkDay:
    def __init__(self, day_name, is_off=False):
        self.day_name = day_name
        self.is_off = is_off
        self.shift_done = False

    def mark_shift_done(self):
        self.shift_done = True

    def get_status_text(self):
        if self.is_off:
            return "OFF"
        if self.shift_done:
            return "Bitti ✔"
        return "09:00\n17:00"

    def get_color(self):
        if self.is_off:
            return "#e74c3c"
        if self.shift_done:
            return "#27ae60"
        return "#2980b9"

    def __repr__(self):
        return f"WorkDay({self.day_name}, off={self.is_off})"