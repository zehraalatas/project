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
        self.db.cursor.execute(
            "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Bekliyor')",
            (sender_name, request_type, detail))
        self.db.conn.commit()

    def get_pending_requests(self):
        self.db.cursor.execute("SELECT * FROM requests WHERE status='Bekliyor'")
        return self.db.cursor.fetchall()

    def update_request_status(self, req_id, status):
        self.db.cursor.execute("SELECT request_type FROM requests WHERE id=?", (req_id,))
        req_type = self.db.cursor.fetchone()[0]

        final_status = status
        if req_type == "Zam" and status == "Onaylandı":
            final_status = "Müdür Onayladı"  # Zamsa patrona ilet

        self.db.cursor.execute("UPDATE requests SET status=? WHERE id=?", (final_status, req_id))
        self.db.conn.commit()

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