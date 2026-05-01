from models.shift import Shift
class HRService:
    def __init__(self, db_manager):
        self.db = db_manager

    def submit_application(self, name, role):
        self.db.cursor.execute("INSERT INTO applications (name, desired_role, status) VALUES (?, ?, 'Bekliyor')",
                               (name, role))
        self.db.conn.commit()

    def get_pending_applications(self):
        self.db.cursor.execute("SELECT * FROM applications WHERE status='Bekliyor'")
        return self.db.cursor.fetchall()

    def process_application(self, app_id, status):
        if status == "Onaylandı":
            self.db.cursor.execute("SELECT name, desired_role FROM applications WHERE id=?", (app_id,))
            app_data = self.db.cursor.fetchone()
            if app_data:
                name, role = app_data
                clean_name = name.lower().strip()
                username = f"{role.lower()} {clean_name}"
                password = f"{clean_name}123"  # OTOMATİK ŞİFRE (Örn: ahmet123)

                try:
                    self.db.cursor.execute(
                        "INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)",
                        (username, password, role, 20000.0, 2, "Pazartesi")
                    )
                except:
                    pass

        self.db.cursor.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        self.db.conn.commit()

    def submit_internal_request(self, sender_name, request_type, detail):
        # 'Bekliyor' yerine 'Müdür Onayı Bekliyor' yazıyoruz
        self.db.cursor.execute(
            "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Müdür Onayı Bekliyor')",
            (sender_name, request_type, detail))
        self.db.conn.commit()

    def get_pending_requests(self):
        self.db.cursor.execute("SELECT * FROM requests WHERE status='Bekliyor'")
        return self.db.cursor.fetchall()

    def update_request_status(self, req_id, status, approver_role):
        self.db.cursor.execute("SELECT sender_name, request_type FROM requests WHERE id=?", (req_id,))
        row = self.db.cursor.fetchone()
        if not row: return False
        sender, req_type = row

        if approver_role == "Müdür":
            if status == "Onaylandı":
                # Müdür onay verince adminin listesine düşmesi için status'ü değiştiriyoruz
                new_status = "Patron Onayı Bekliyor"
            else:
                new_status = "Reddedildi"

        elif approver_role == "Patron":
            if status == "Onaylandı":
                new_status = "Kesin Onaylandı"
                # İşe alım veya izin gününü burada tetikleyebiliriz
            else:
                new_status = "Reddedildi"

        self.db.cursor.execute("UPDATE requests SET status=? WHERE id=?", (new_status, req_id))
        self.db.conn.commit()
        return sender, req_type, new_status
    # YENİ: Takvim ve İşten Çıkarma Fonksiyonları
    def set_off_day_by_username(self, username, off_day):
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE username=?", (off_day, username))
        self.db.conn.commit()

    def set_off_day_by_id(self, user_id, off_day):
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE id=?", (off_day, user_id))
        self.db.conn.commit()

    def fire_employee(self, user_id):
        self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.db.conn.commit()

    def get_forwarded_raises(self):
        self.db.cursor.execute("SELECT * FROM requests WHERE status='Müdür Onayladı' AND request_type='Zam'")
        return self.db.cursor.fetchall()

    def final_approve_raise(self, req_id, percent):
        # Talebi gönderen çalışanı bul
        self.db.cursor.execute("SELECT sender_name FROM requests WHERE id=?", (req_id,))
        sender = self.db.cursor.fetchone()[0]

        # Mevcut maaşı al
        self.db.cursor.execute("SELECT salary FROM users WHERE username=?", (sender,))
        result = self.db.cursor.fetchone()

        if result:
            current_salary = result[0]
            new_salary = round(current_salary * (1 + percent / 100))
            self.db.cursor.execute("UPDATE users SET salary=? WHERE username=?", (new_salary, sender))

        self.db.cursor.execute("UPDATE requests SET status='Kesin Onaylandı' WHERE id=?", (req_id,))
        self.db.conn.commit()

        return current_salary, new_salary  # UI'da göstermek için

    def check_off_day_conflict(self, user_id, role, new_off_day):
        # O roldeki toplam çalışan sayısı (kendisi dahil)
        self.db.cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role=? AND role NOT IN ('Patron', 'Müdür')
        """, (role,))
        total_same_role = self.db.cursor.fetchone()[0]

        # Rolde tek kişiyse izin günü hiç olamaz
        if total_same_role <= 1:
            return False, f"Sistemde tek {role} var, izin günü atanamaz!"

        # Birden fazla kişi varsa — o gün çakışma kontrolü
        self.db.cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role=? AND off_day=? AND id!=?
        """, (role, new_off_day, user_id))
        already_off_count = self.db.cursor.fetchone()[0]

        working_that_day = (total_same_role - 1) - already_off_count  # -1: kendisi izinde

        if working_that_day < 1:
            return False, f"O gün tüm {role}lar izinli! Başka bir gün seçin."

        return True, "OK"

    def get_available_off_day(self, user_id, role):
        """
        O roldeki diğer çalışanların izin günlerine bakar,
        çakışmayan ilk günü döndürür. Bulamazsa None döner.
        """
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        # O roldeki diğer kişilerin izin günleri
        self.db.cursor.execute(
            "SELECT off_day FROM users WHERE role=? AND id!=?", (role, user_id)
        )
        taken_days = {row[0] for row in self.db.cursor.fetchall()}

        # Çakışmayan ilk günü bul
        for day in days:
            if day not in taken_days:
                return day

        return None  # Tüm günler dolu

    def save_shift_record(self, user_id, username):
        import datetime
        today = datetime.date.today().isoformat()

        # shifts tablosuna yeni bir satır ekliyoruz
        self.db.cursor.execute(
            "INSERT INTO shifts (user_id, username, date, hours) VALUES (?, ?, ?, ?)",
            (user_id, username, today, 8)  # Standart 8 saatlik çalışma
        )
        self.db.conn.commit()

    # services/hr_service.py içine ekle:
    def log_status(self, user_id, username, status):
        import datetime
        today = datetime.date.today().isoformat()

        # Bugün için zaten kayıt var mı kontrol et (Mükerrer kayıt olmasın)
        self.db.cursor.execute("SELECT id FROM shifts WHERE user_id=? AND date=?", (user_id, today))
        if not self.db.cursor.fetchone():
            self.db.cursor.execute(
                "INSERT INTO shifts (user_id, username, date, status) VALUES (?, ?, ?, ?)",
                (user_id, username, today, status)
            )
            self.db.conn.commit()

    def get_all_shifts(self):
        self.db.cursor.execute("SELECT id, user_id, username, date, status FROM shifts ORDER BY date DESC")
        rows = self.db.cursor.fetchall()

        # Ham veriyi (tuple) Shift nesnelerine dönüştürüyoruz (Mapping)
        return [Shift(r[0], r[1], r[2], r[3], r[4]) for r in rows]

    def submit_manager_request(self, sender_name, request_type, detail):
        """Müdürün talepleri doğrudan Patron'a gider"""
        self.db.cursor.execute(
            "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Patron Onayı Bekliyor')",
            (sender_name, request_type, detail))
        self.db.conn.commit()