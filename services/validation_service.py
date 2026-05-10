import re

class ValidationService:
    def __init__(self):
        pass

    def is_valid_email(self, email):
        email = str(email).strip().lower()

        if "@" in email and email.endswith(".com"):
            parts = email.split("@")
            if len(parts) == 2 and parts[0] != "" and parts[1] != "":
                return True

        return False

    def is_valid_phone(self, phone):
        phone = str(phone).strip()
        return phone.startswith("05") and len(phone) == 11 and phone.isdigit()

    def is_valid_date_range(self, date_text):
        pattern = r"^\d{4}-\d{4}$"
        if re.match(pattern, date_text):
            years = date_text.split("-")
            start = int(years[0])
            end = int(years[1])

            current_year = 2026

            if start > end:
                return False, "Start year cannot be greater than end year!"

            if start < 1950 or end > current_year:
                return False, f"Years must be between 1950 and {current_year}!"

            return True,""
        return False, "Format must be YYYY-YYYY (e.g. 2018-2022)"