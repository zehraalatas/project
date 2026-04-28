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