class CV:
    def __init__(self, name, surname, gender, email, phone, experiences, notes=""):
        self.name = name
        self.surname = surname
        self.gender = gender
        self.email = email
        self.phone = phone
        self.experiences = experiences  # Artık bu bir LISTE: [{"company": "X", "pos": "Y", "date": "Z"}, ...]
        self.notes = notes