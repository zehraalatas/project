import json
from models.cv import CV
from models.application import Application

class HRService:
    def __init__(self, db_manager):
        self.db = db_manager

    def submit_application(self, cv_obj, role):
        exp_data = cv_obj.experiences

        query = """INSERT INTO applications
                   (name, surname, gender, email, phone, experience, notes, desired_role, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')"""
        self.db.cursor.execute(query, (
            cv_obj.name, cv_obj.surname, cv_obj.gender, cv_obj.email,
            cv_obj.phone, exp_data, cv_obj.notes, role
        ))
        self.db.conn.commit()

    def get_pending_applications(self):
        query = "SELECT id, name, surname, gender, email, phone, experience, notes, desired_role FROM applications WHERE status='Pending'"
        self.db.cursor.execute(query)
        rows = self.db.cursor.fetchall()

        apps = []
        for r in rows:
            try:
                raw_exp = r[6]
                if not raw_exp or raw_exp == "No Experience":
                    parsed_exp = []
                else:
                    try:
                        parsed_exp = json.loads(raw_exp)
                        if isinstance(parsed_exp, str):
                            parsed_exp = json.loads(parsed_exp)
                        if not isinstance(parsed_exp, list):
                            parsed_exp = []
                    except Exception:
                        parsed_exp = []

                cv = CV(
                    name=r[1],
                    surname=r[2],
                    gender=r[3],
                    email=r[4],
                    phone=r[5],
                    experiences=parsed_exp,
                    notes=r[7]
                )
                apps.append(Application(r[0], r[8], "Pending", cv))
            except Exception as e:
                print(f"Error: {e}")
                continue
        return apps

    def process_application(self, app_id, status):
        if status == "Approved":
            query = "SELECT name, surname, desired_role FROM applications WHERE id=?"
            self.db.cursor.execute(query, (app_id,))
            app_data = self.db.cursor.fetchone()

            if app_data:
                name, surname, role = app_data

                clean_name = name.lower().strip().replace(" ", "")
                clean_surname = surname.lower().strip().replace(" ", "")

                base_username = f"{clean_name}_{clean_surname}"
                final_username = base_username
                counter = 1

                while True:
                    self.db.cursor.execute("SELECT id FROM users WHERE username=?", (final_username,))
                    if not self.db.cursor.fetchone():
                        break
                    counter += 1
                    final_username = f"{base_username}{counter}"

                password = f"{clean_name}123"

                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                best_day = "Monday"
                min_count = float('inf')

                for d in days:
                    self.db.cursor.execute(
                        "SELECT COUNT(*) FROM users WHERE role=? AND off_day=?",
                        (role, d)
                    )
                    count = self.db.cursor.fetchone()[0]

                    if count < min_count:
                        min_count = count
                        best_day = d

                    if count == 0:
                        best_day = d
                        break

                try:
                    self.db.cursor.execute(
                        "INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)",
                        (final_username, password, role, 20000.0, 2, best_day)
                    )
                except Exception as e:
                    print(f"Error: {e}")

        self.db.cursor.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        self.db.conn.commit()

    def submit_internal_request(self, sender_name, request_type, detail):
        query = "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Pending Manager')"
        self.db.cursor.execute(query, (sender_name, request_type, detail))
        self.db.conn.commit()

    def update_request_status(self, req_id, status, approver_role):
        self.db.cursor.execute("SELECT sender_name, request_type FROM requests WHERE id=?", (req_id,))
        row = self.db.cursor.fetchone()
        if not row: return False
        sender, req_type = row

        new_status = status

        if approver_role == "Manager":
            if status == "Approved":
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
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE username=?", (new_day, username))
        self.db.conn.commit()

    def set_off_day_by_id(self, user_id, new_day):
        self.db.cursor.execute("UPDATE users SET off_day=? WHERE id=?", (new_day, user_id))
        self.db.conn.commit()

    def fire_employee(self, user_id):
        self.db.cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
        row = self.db.cursor.fetchone()
        if not row:
            return
        fired_role = row[0]

        self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.db.conn.commit()

        self.db.cursor.execute(
            "SELECT id, off_day FROM users WHERE role=?", (fired_role,)
        )
        remaining = self.db.cursor.fetchall()

        if len(remaining) < 2:
            return

        off_days = [r[1] for r in remaining]
        if len(set(off_days)) == 1:
            all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for idx, (uid, _) in enumerate(remaining):
                new_day = all_days[idx % len(all_days)]
                self.db.cursor.execute("UPDATE users SET off_day=? WHERE id=?", (new_day, uid))
            self.db.conn.commit()

    def check_off_day_conflict(self, user_id, role, new_off_day):
        self.db.cursor.execute("""
                               SELECT COUNT(*)
                               FROM users
                               WHERE role = ?
                                 AND role NOT IN ('Boss', 'Manager')
                               """, (role,))
        total_same_role = self.db.cursor.fetchone()[0]

        if total_same_role <= 1:
            return False, f"Only one {role} exists. Coverage required!"

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

    def submit_manager_request(self, sender_name, request_type, detail):
        query = "INSERT INTO requests (sender_name, request_type, detail, status) VALUES (?, ?, ?, 'Pending Boss')"
        self.db.cursor.execute(query, (sender_name, request_type, detail))
        self.db.conn.commit()

    def get_role_count(self, role_name):
        query = "SELECT COUNT(*) FROM users WHERE role = ?"
        self.db.cursor.execute(query, (role_name,))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0

