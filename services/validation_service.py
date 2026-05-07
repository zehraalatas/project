import re

class ValidationService:
    def __init__(self):
        pass

    def is_empty(self, *args):
        """Herhangi bir alan boş mu kontrol eder"""
        for field in args:
            if not str(field).strip():
                return True
        return False

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
        """Format kontrolü: YYYY-YYYY (Örn: 2018-2022)"""
        import re
        # 4 rakam - 4 rakam formatını kontrol eder
        pattern = r"^\d{4}-\d{4}$"
        if re.match(pattern, date_text):
            years = date_text.split("-")
            # Başlangıç yılı bitişten büyük olamaz
            if int(years[0]) <= int(years[1]):
                return True
        return False