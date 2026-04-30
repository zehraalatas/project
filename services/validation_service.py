class ValidationService:
    @staticmethod
    def is_valid_username(username):
        return bool(username) and len(username) >= 3

    @staticmethod
    def is_valid_password(password):
        return bool(password) and len(password) >= 6

    @staticmethod
    def is_valid_percent(value):
        try:
            p = float(value)
            return 0 < p <= 100
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_numeric(value):
        return str(value).replace(".", "", 1).isdigit()