import re

class ValidationService:
    def __init__(self):
        pass

    def is_valid_email(self, email):
        """Maili temizler ve kontrol eder"""
        # 1. Önce veriyi temizleyelim (Başındaki sonundaki gizli boşlukları atar)
        email = str(email).strip().lower()

        # 2. Daha esnek bir kontrol:
        # En az bir karakter + @ + en az bir karakter + .com
        if "@" in email and email.endswith(".com"):
            # '@' işaretinden önce ve sonra karakter var mı?
            parts = email.split("@")
            if len(parts) == 2 and parts[0] != "" and parts[1] != "":
                return True

        return False

    def is_valid_phone(self, phone):
        """05 ile başlayan ve tam 11 haneli (0 dahil) kontrolü"""
        # Kullanıcı 05... diye girdiği için 11 karakter kontrolü yapıyoruz
        # Eğer sadece 5... kısmını istiyorsan 10 karakter yapabilirsin
        phone = str(phone).strip()
        return phone.startswith("05") and len(phone) == 11 and phone.isdigit()

    def is_valid_date_range(self, date_text):
        pattern = r"^\d{4}-\d{4}$"
        if re.match(pattern, date_text):
            years = date_text.split("-")
            start = int(years[0])
            end = int(years[1])

            current_year = 2026

            # Başlangıç bitiş kontrolü (zaten vardı)
            if start > end:
                return False, "Start year cannot be greater than end year!"

            # Makul yıl aralığı kontrolü
            if start < 1950 or end > current_year:
                return False, f"Years must be between 1950 and {current_year}!"


            return True,""
        return False, "Format must be YYYY-YYYY (e.g. 2018-2022)"