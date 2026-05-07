import datetime
from models.shift import Shift


class HRService:
    def __init__(self, db_manager):
        self.db = db_manager

    def submit_application(self, name, role):
        """Adds a new job application to the system with 'Pending' status"""
        query = "INSERT INTO applications (name, desired_role, status) VALUES (?, ?, 'Pending')"
        self.db.cursor.execute(query, (name, role))
        self.db.conn.commit()

    def get_pending_applications(self):
        """Fetches all job applications waiting for review"""
        self.db.cursor.execute("SELECT * FROM applications WHERE status='Pending'")
        return self.db.cursor.fetchall()

    def process_application(self, app_id, status):
        """Finalizes the application. If 'Approved', automatically creates a new employee account."""
        if status == "Approved":
            self.db.cursor.execute("SELECT name, desired_role FROM applications WHERE id=?", (app_id,))
            app_data = self.db.cursor.fetchone()

            if app_data:
                name, role = app_data
                clean_name = name.lower().strip().replace(" ", "")

                # --- İSİM ÇAKIŞMASI KONTROL DÖNGÜSÜ ---
                base_username = f"{role.lower()}_{clean_name}"
                final_username = base_username
                counter = 1

                while True:
                    # Veritabanında bu username var mı diye bakıyoruz
                    self.db.cursor.execute("SELECT id FROM users WHERE username=?", (final_username,))
                    if not self.db.cursor.fetchone():
                        # Eğer yoksa (boşsa), döngüden çık, doğru ismi bulduk!
                        break

                    # Eğer varsa, sayacı 1 artır ve ismin sonuna ekle (Örn: waiter_ahmet2)
                    counter += 1
                    final_username = f"{base_username}{counter}"

                # Şifreyi de yeni isme göre belirleyelim (Ahmet2 ise şifresi ahmet2123 olsun)
                password_prefix = f"{clean_name}{counter if counter > 1 else ''}"
                password = f"{password_prefix}123"

                try:
                    # New employees start with a default salary and Monday off-day
                    self.db.cursor.execute(
                        "INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)",
                        (final_username, password, role, 20000.0, 2, "Monday")
                    )
                except Exception as e:
                    print(f"Error creating user: {e}")

        # Update the application table with the final decision
        self.db.cursor.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        self.db.conn.commit()

    def submit_internal_request(self, sender_name, request_type, detail):
        """Employees send requests to the Manager first"""
        query = "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Pending Manager')"
        self.db.cursor.execute(query, (sender_name, request_type, detail))
        self.db.conn.commit()

    def update_request_status(self, req_id, status, approver_role):
        """Updates request lifecycle: Staff -> Manager -> Boss -> Final"""
        self.db.cursor.execute("SELECT sender_name, request_type FROM requests WHERE id=?", (req_id,))
        row = self.db.cursor.fetchone()
        if not row: return False
        sender, req_type = row

        new_status = status  # Default

        if approver_role == "Manager":
            if status == "Approved":
                # Forwards to Boss for final confirmation
                new_status = "Pending Boss"
            else:
                new_status = "Rejected"

        elif approver_role == "Boss":
            if status == "Approved":
                new_status = "Finalized"
            else:
                new_status = "Rejected"

        self.db.cursor.execute("UPDATE requests SET status=? WHERE id=?", (new_status, req_id))
        self.db.conn.commit()
        return sender, req_type, new_status

    def set_off_day_by_username(self, username, new_day):
        """Kullanıcı adına göre izin gününü günceller (Patron Onayı İçin)"""
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE username=?", (new_day, username))
        self.db.conn.commit()

    def set_off_day_by_id(self, user_id, new_day):
        """Kullanıcı ID'sine göre izin gününü günceller (Patron Direkt Değiştirirse)"""
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE id=?", (new_day, user_id))
        self.db.conn.commit()

    def fire_employee(self, user_id):
        """Removes an employee account from the database"""
        self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.db.conn.commit()

    def check_off_day_conflict(self, user_id, role, new_off_day):
        """Checks if a role has enough coverage for the selected off-day"""
        # Excluding Boss and Manager from coverage rules
        self.db.cursor.execute("""
                               SELECT COUNT(*)
                               FROM users
                               WHERE role = ?
                                 AND role NOT IN ('Boss', 'Manager')
                               """, (role,))
        total_same_role = self.db.cursor.fetchone()[0]

        if total_same_role <= 1:
            return False, f"Only one {role} exists. Coverage required!"

        # Check how many others in the same role are already off on that day
        self.db.cursor.execute("""
                               SELECT COUNT(*)
                               FROM users
                               WHERE role = ?
                                 AND off_day = ?
                                 AND id!=?
                               """, (role, new_off_day, user_id))
        already_off_count = self.db.cursor.fetchone()[0]

        remaining_workers = (total_same_role - 1) - already_off_count

        if remaining_workers < 1:
            return False, "Conflict: No coverage available for this day!"

        return True, "Success"

    def log_status(self, user_id, username, status):
        """Logs daily working status into the shifts table"""
        today = datetime.date.today().isoformat()

        # Prevent duplicate logs for the same day
        self.db.cursor.execute("SELECT id FROM shifts WHERE user_id=? AND date=?", (user_id, today))
        if not self.db.cursor.fetchone():
            self.db.cursor.execute(
                "INSERT INTO shifts (user_id, username, date, status) VALUES (?, ?, ?, ?)",
                (user_id, username, today, status)
            )
            self.db.conn.commit()

    def get_all_shifts(self):
        """Fetches all shift history for the Boss tracking report"""
        self.db.cursor.execute("SELECT id, user_id, username, date, status FROM shifts ORDER BY date DESC")
        rows = self.db.cursor.fetchall()
        # Mapping results to the Shift object list (Lesson Topic: List Comprehension)
        return [Shift(r[0], r[1], r[2], r[3], r[4]) for r in rows]

    def submit_manager_request(self, sender_name, request_type, detail):
        """Manager requests bypass themselves and go directly to the Boss"""
        query = "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Pending Boss')"
        self.db.cursor.execute(query, (sender_name, request_type, detail))
        self.db.conn.commit()

    def get_role_count(self, role_name):
        query = "SELECT COUNT(*) FROM users WHERE role = ?"
        self.db.cursor.execute(query, (role_name,))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0