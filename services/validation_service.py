class ValidationService:
    def __init__(self):
        # self ile yazıldığında ileride gerekirse buraya
        # kısıtlamalar (min_length=3 gibi) ekleyebilirsin.
        pass

    def is_valid_username(self, username):
        """Validates username using instance context"""
        return bool(username) and len(str(username).strip()) >= 3

    def is_valid_password(self, password):
        """Validates password using instance context"""
        return bool(password) and len(str(password)) >= 6

    def is_valid_percent(self, value):
        """Validates percentage using instance context"""
        try:
            p = float(value)
            return 0 < p <= 100
        except (ValueError, TypeError):
            return False

    def is_numeric(self, value):
        """Helper to check if input is numeric"""
        return str(value).replace(".", "", 1).isdigit()