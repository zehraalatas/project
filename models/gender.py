class Gender:
    def __init__(self):
        # Sabitleri sınıf içinde tanımlıyoruz
        self.FEMALE = "Female"
        self.MALE = "Male"
        self.OTHER = "Other"
        self.PREFER_NOT_TO_SAY = "Prefer not to say"

    def get_all_values(self):
        """ComboBox'lar için tüm değerleri liste olarak döndürür"""
        return [
            self.FEMALE,
            self.MALE,
            self.OTHER,
            self.PREFER_NOT_TO_SAY
        ]

    def get_icon(self, gender_value):
        """Cinsiyete göre ikon döndüren yardımcı metot (self ile)"""
        icons = {
            self.FEMALE: "👩‍💼",
            self.MALE: "👨‍💼",
            self.OTHER: "🌈",
            self.PREFER_NOT_TO_SAY: "👤"
        }
        # Eğer gelen değer listede yoksa varsayılan olarak 👤 döner
        return icons.get(gender_value, "👤")