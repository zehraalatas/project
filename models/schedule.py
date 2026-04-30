from models.work_day import WorkDay


class Schedule:
    def __init__(self, user_id, off_day_name):
        self.user_id = user_id
        self.DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        # Haftalık programı WorkDay nesneleriyle dolduruyoruz
        self.weekly_plan = []
        for d in self.DAYS:
            is_off = (d == off_day_name)
            # Her gün için bir WorkDay nesnesi oluşturuluyor
            self.weekly_plan.append(WorkDay(d, is_off=is_off))

    def get_day_status(self, day_name):
        for wd in self.weekly_plan:
            if wd.day_name == day_name:
                return wd.get_summary()
        return "Gün bulunamadı"