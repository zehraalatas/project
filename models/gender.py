class Gender:
    def __init__(self):
        self.FEMALE = "Female"
        self.MALE = "Male"
        self.OTHER = "Other"
        self.PREFER_NOT_TO_SAY = "Prefer not to say"

    def get_all_values(self):
        return [
            self.FEMALE,
            self.MALE,
            self.OTHER,
            self.PREFER_NOT_TO_SAY
        ]
