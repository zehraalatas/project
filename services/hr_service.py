from models.cv import CV
from models.application import Application
from models.shift import Shift
from datetime import datetime
import json


class HRService:
    def __init__(self, db_manager):
        self.db = db_manager

    def submit_application(self, cv_obj, role):
        # Deneyim listesini stringe çeviriyoruz (Serialization)
        exp_json = json.dumps(cv_obj.experiences)

        query = """INSERT INTO applications
                   (name, surname, gender, email, phone, experience, notes, desired_role, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')"""
        self.db.cursor.execute(query, (
            cv_obj.name, cv_obj.surname, cv_obj.gender, cv_obj.email,
            cv_obj.phone, exp_json, cv_obj.notes, role
        ))
        self.db.conn.commit()

    def get_pending_applications(self):
        query = "SELECT id, name, surname, gender, email, phone, experience, notes, desired_role FROM applications WHERE status='Pending'"
        self.db.cursor.execute(query)
        rows = self.db.cursor.fetchall()

        from models.cv import CV
        from models.application import Application

        apps = []
        for r in rows:
            try:
                # r[6] veritabanındaki 'experience' kolonudur
                cv = CV(
                    name=r[1],
                    surname=r[2],
                    gender=r[3],
                    email=r[4],
                    phone=r[5],
                    experiences=r[6], # Modeldeki isim 'experiences'
                    notes=r[7]
                )
                # Sınıfındaki parametre sırası: id, role, status, cv_obj
                apps.append(Application(r[0], r[8], "Pending", cv))
            except Exception as e:
                print(f"Hata: {e}")
                continue
        return apps

    def process_application(self, app_id, status):
        """Başvuruyu sonuçlandırır. Eğer 'Approved' ise CV verileriyle kullanıcı hesabı açar."""
        if status == "Approved":
            # 1. Veritabanından adayın tüm CV bilgilerini çekiyoruz
            query = "SELECT name, surname, desired_role FROM applications WHERE id=?"
            self.db.cursor.execute(query, (app_id,))
            app_data = self.db.cursor.fetchone()

            if app_data:
                name, surname, role = app_data

                # 2. f-string ile Temiz Kullanıcı Adı Oluşturma
                # Küçük harfe çeviriyoruz, boşlukları siliyoruz (Örn: "Ömer Demir" -> "omer_demir")
                clean_name = name.lower().strip().replace(" ", "")
                clean_surname = surname.lower().strip().replace(" ", "")

                base_username = f"{clean_name}_{clean_surname}"  # İşte bahsettiğim f-string burası!
                final_username = base_username
                counter = 1

                # 3. İsim Çakışması Kontrolü (Aynı isimde başka çalışan varsa)
                while True:
                    self.db.cursor.execute("SELECT id FROM users WHERE username=?", (final_username,))
                    if not self.db.cursor.fetchone():
                        break
                    counter += 1
                    final_username = f"{base_username}{counter}"

                # 4. Şifre Oluşturma (Örn: odemir123)
                # İsmin ilk harfi + soyisim + 123
                password = f"{clean_name}123"

                try:
                    # Yeni çalışanı varsayılan maaş (20.000) ve izin günüyle ekliyoruz
                    self.db.cursor.execute(
                        "INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)",
                        (final_username, password, role, 20000.0, 2, "Monday")
                    )
                    print(f"Account Created: {final_username} / Password: {password}")
                except Exception as e:
                    print(f"Error creating user: {e}")

        # 5. Başvuru tablosunu güncelle (Status: Approved/Rejected)
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