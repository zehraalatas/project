import customtkinter as ctk
import datetime
import json  # Dosyanın en başında mutlaka olmalı

class PatronDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        # 1. Main frame for statistics cards at the top
        self.stat_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.stat_frame.pack(pady=20, padx=20, fill="x")

        # 2. Load statistics from services
        self.update_stat_cards()

        self.tabview = ctk.CTkTabview(app)
        self.tabview.pack(pady=5, padx=20, fill="both", expand=True)

        # Tabs updated to match English schema
        self.tab_staff_manage = self.tabview.add("👥 Staff & Salary")
        self.tab_approvals = self.tabview.add("📩 Pending Approvals")
        self.tab_applications = self.tabview.add("📝 Job Applications")
        self.tab_reports = self.tabview.add("📊 Performance Tracking")

        # Load initial data for all tabs
        self.load_staff_management()
        self.load_manager_approvals()
        self.load_job_applications()
        self.load_job_applications()

        # Listen for tab changes (specifically for the tracking tab)
        self.tabview.configure(command=self.on_tab_change)

        # Footer buttons
        self.board_btn = ctk.CTkButton(app, text="📝 Company Notice Board", command=self.open_notice_board,
                                       fg_color="#8e44ad", width=200)
        self.board_btn.pack(side="top", pady=(5, 10))

        self.logout_btn = ctk.CTkButton(app, text="Secure Logout", command=self.app.show_login_screen,
                                        fg_color="darkred")
        self.logout_btn.pack(side="bottom", pady=10)

    def update_stat_cards(self):
        """Refreshes the dynamic statistics at the top of the dashboard"""
        for widget in self.stat_frame.winfo_children():
            widget.destroy()

        active_count = self.app.report_service.get_active_employee_count()
        total_cost = self.app.report_service.get_total_salary_cost()

        # Stat cards
        self.create_stat_card(self.stat_frame, "Daily Revenue", "14.250 ₺", "#2ecc71", 0)
        self.create_stat_card(self.stat_frame, "Salary Costs", f"{total_cost:,.0f} ₺", "#e74c3c", 1)
        self.create_stat_card(self.stat_frame, "Active Staff", f"{active_count}", "#f1c40f", 2)

    def create_stat_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, border_width=2, border_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="gray").pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=color).pack(pady=(0, 10))

    def load_staff_management(self):
        """Lists staff for management (excluding the Boss)"""
        for widget in self.tab_staff_manage.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_staff_manage, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        self.app.db_manager.cursor.execute(
            "SELECT id, username, role, salary, off_day FROM users WHERE role != 'Boss'")
        staff_list = self.app.db_manager.cursor.fetchall()

        english_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for person in staff_list:
            p_id, name, role, salary, current_off = person

            # --- YENİ MANTIK: O rolde kaç kişi var? ---
            # HRService içindeki metodu çağırıyoruz
            role_count = self.app.hr_service.get_role_count(role)

            row = ctk.CTkFrame(scroll, corner_radius=8, border_width=1, border_color="#34495e")
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkLabel(row, text=f"👤 {name.capitalize()} ({role})", font=("Arial", 13, "bold"),
                         width=160, anchor="w").pack(side="left", padx=10)

            ctk.CTkLabel(row, text=f"{salary:,.0f} ₺", font=("Arial", 13, "bold"),
                         text_color="#2ecc71", width=90).pack(side="left", padx=5)

            # Maaş butonları kalsın...
            ctk.CTkButton(row, text="+1k", width=45, fg_color="#27ae60",
                          command=lambda i=p_id, s=salary: self.change_salary(i, s, 1000)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="-1k", width=45, fg_color="#d35400",
                          command=lambda i=p_id, s=salary: self.change_salary(i, s, -1000)).pack(side="left", padx=2)

            custom_entry = ctk.CTkEntry(row, width=70, placeholder_text="Amt")
            custom_entry.pack(side="left", padx=(10, 2))

            # Mevcut Artı (+) Butonu
            ctk.CTkButton(row, text="+", width=30, fg_color="#2ecc71",
                          command=lambda i=p_id, s=salary, e=custom_entry: self.apply_custom_salary(i, s, e.get(),
                                                                                                    1)).pack(
                side="left", padx=2)

            # --- YENİ EKLENEN EKSİ (-) BUTONU ---
            ctk.CTkButton(row, text="-", width=30, fg_color="#e74c3c",
                          command=lambda i=p_id, s=salary, e=custom_entry: self.apply_custom_salary(i, s, e.get(),
                                                                                                    -1)).pack(
                side="left", padx=2)
            # ------------------------------------

            # --- DYNAMIC AREA İS HERE ---
            if role_count <= 1 and role not in ('Boss', 'Manager'):
                # If the role is only 1 person: COMBOBOX BECOME RED
                only_label = ctk.CTkLabel(row, text=f"ONLY {role.upper()}",
                                          text_color="#e74c3c", font=("Arial", 12, "bold"), width=110)
                only_label.pack(side="left", padx=(20, 5))
            else:
                # More than 1 person: COMBOBOX (CHOOSE A DAY)
                combo = ctk.CTkComboBox(row, values=english_days, width=110)
                combo.set(current_off)
                combo.pack(side="left", padx=(20, 5))

                ctk.CTkButton(row, text="Save", width=70, fg_color="#3498db",
                              command=lambda i=p_id, c=combo: self.update_day(i, c.get())).pack(side="left", padx=5)

    def apply_custom_salary(self, p_id, current_salary, amount_str, multiplier):
        if not amount_str.replace('.', '', 1).isdigit():
            win = ctk.CTkToplevel(self.app)
            win.geometry("250x120")
            win.title("Error")
            win.attributes("-topmost", True)
            ctk.CTkLabel(win, text="⚠️ Enter a valid number!", text_color="#e74c3c").pack(pady=20)
            ctk.CTkButton(win, text="OK", command=win.destroy).pack()
            return

        amount = float(amount_str) * multiplier
        self.change_salary(p_id, current_salary, amount)

    def load_manager_approvals(self):
        """Lists employee requests waiting for final Boss confirmation"""
        for widget in self.tab_approvals.winfo_children(): widget.destroy()

        # CRITICAL: Updated status to 'Pending Boss' to match new HRService
        self.app.db_manager.cursor.execute("SELECT * FROM requests WHERE status='Pending Boss'")
        requests = self.app.db_manager.cursor.fetchall()

        if not requests:
            ctk.CTkLabel(self.tab_approvals, text="No pending approvals.", text_color="gray").pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.tab_approvals, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Local type mapping
        type_map = {"Leave": "Leave Request", "Salary": "Salary Raise"}

        for req in requests:
            r_id, sender, r_type, detail, status = req
            frame = ctk.CTkFrame(scroll)
            frame.pack(pady=5, padx=20, fill="x")

            eng_type = type_map.get(r_type, r_type)
            ctk.CTkLabel(frame, text=f"👤 {sender.capitalize()} - {eng_type} ({detail})",
                         font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=10)

            ctk.CTkButton(frame, text="Reject ❌", width=90, fg_color="#e74c3c",
                          command=lambda r=r_id, s=sender, rt=r_type: self.reject_request(r, s, rt)).pack(side="right",
                                                                                                          padx=10)

            if r_type == "Salary":
                ctk.CTkButton(frame, text="Set Raise", width=120, fg_color="#2ecc71",
                              command=lambda r=r_id, s=sender: self.open_raise_popup(r, s)).pack(side="right", padx=10)
            else:
                ctk.CTkButton(frame, text="Final Approve", width=120, fg_color="#3498db",
                              command=lambda r=r_id, s=sender, rt=r_type, d=detail: self.final_confirm(r, s, rt, d)).pack(side="right", padx=10)

    def final_confirm(self, req_id, sender, r_type, detail):
        """Talebi onaylar ve sayfayı anında yeniler"""

        if r_type == "Leave":
            # 1. Kullanıcıyı bul
            self.app.db_manager.cursor.execute("SELECT id, role FROM users WHERE username=?", (sender,))
            user_info = self.app.db_manager.cursor.fetchone()

            if user_info:
                u_id, u_role = user_info

                # Boss ve Manager hariç diğerleri için vardiya çakışması kontrolü
                if u_role not in ('Boss', 'Manager'):
                    is_valid, error_msg = self.app.hr_service.check_off_day_conflict(u_id, u_role, detail)

                    if not is_valid:
                        # KURAL: Eğer uygun değilse işlemi burada kes!
                        pop = ctk.CTkToplevel(self.app)
                        pop.title("Coverage Error")
                        pop.geometry("300x150")
                        pop.attributes("-topmost", True)
                        ctk.CTkLabel(pop, text=f"⚠️ {error_msg}", text_color="#e74c3c", font=("Arial", 12, "bold"),
                                     wraplength=260).pack(pady=20, padx=20)
                        ctk.CTkButton(pop, text="OK", command=pop.destroy, fg_color="#34495e").pack()
                        return  # İşlemi durdurur

                # 2. SORUN YOKSA: İzin gününü güncelle
                self.app.hr_service.set_off_day_by_username(sender, detail)
                msg = f"Your leave ({detail}) was finalized and approved by the Boss! ✅"
            else:
                msg = "User not found! ❌"
        else:
            msg = "Your request was finalized and approved! ✅"

        # 3. Talebin durumunu 'Finalized' yap
        self.app.hr_service.update_request_status(req_id, "Approved", "Boss")

        # 4. KRİTİK NOKTA: Arayüzü anında yenile
        self.load_manager_approvals()  # Onaylar sekmesini yenile
        self.load_staff_management()  # Personel & Maaş sekmesini yenile (İzin günü burada değişir)
        self.update_stat_cards()  # Üstteki kartları yenile

        # Bildirim gönder
        self.app.notification_service.send(sender, msg)

    def reject_request(self, req_id, sender, r_type):
        """Rejects a leave or salary request and notifies the user"""
        # Veritabanında durumu 'Rejected' olarak güncelle
        self.app.hr_service.update_request_status(req_id, "Rejected", "Boss")

        # Talep türüne göre çalışana gidecek kırmızı bildirim mesajını hazırla
        display_type = "Leave" if r_type == "Leave" else "Salary Raise"
        msg = f"Your {display_type} request was rejected by the Boss. ❌"

        # Bildirimi gönder ve ekranı yenile
        self.app.notification_service.send(sender, msg)
        self.load_manager_approvals()

    def load_job_applications(self):
        for widget in self.tab_applications.winfo_children():
            widget.destroy()

        apps = self.app.hr_service.get_pending_applications()

        for a in apps:
            # --- KORUMA EKLEDİK ---
            # Eğer 'a' bir nesne değilse veya içindeki cv bir nesne değilse atla
            if not a or isinstance(a, str) or isinstance(a.cv, str):
                continue
            # ----------------------

            row = ctk.CTkFrame(self.tab_applications)
            row.pack(fill="x", pady=5, padx=20)

            # Artık burada güvenle name ve surname çağırabiliriz
            ctk.CTkLabel(row, text=f"👤 {a.cv.name} {a.cv.surname} - {a.desired_role}").pack(side="left", padx=10)

            # View CV Butonu
            ctk.CTkButton(row, text="View CV 📄", width=100, fg_color="#8e44ad",
                          command=lambda obj=a: self.show_cv_popup(obj)).pack(side="right", padx=5)
    def process_hire(self, app_id, status):
        self.app.hr_service.process_application(app_id, status)
        self.load_job_applications()
        self.update_stat_cards()
        self.load_staff_management()

    def open_raise_popup(self, req_id, sender):
        win = ctk.CTkToplevel(self.app)
        win.title("Manage Salary Raise")
        win.geometry("350x280")
        win.grab_set()
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=f"💰 Raise for {sender.capitalize()}", font=("Arial", 15, "bold")).pack(pady=(20, 10))

        type_var = ctk.StringVar(value="Net Amount (₺)")
        combo = ctk.CTkComboBox(win, values=["Net Amount (₺)", "Percentage (%)"], variable=type_var, width=180)
        combo.pack(pady=5)

        entry = ctk.CTkEntry(win, placeholder_text="Enter value...", width=180)
        entry.pack(pady=10)

        # Label for error messages
        error_lbl = ctk.CTkLabel(win, text="", font=("Arial", 11, "bold"))
        error_lbl.pack(pady=2)

        def confirm():
            val_str = entry.get().strip()

            # 1. Is it a number
            if not val_str.replace('.', '', 1).isdigit():
                error_lbl.configure(text="⚠️ Please enter a valid number!", text_color="#e74c3c")
                return

            val = float(val_str)
            raise_type = type_var.get()

            # 2 If it is a percent check for is in 0 and 100
            if "Percentage" in raise_type:
                if not (0 < val <= 100):
                    error_lbl.configure(text="⚠️ Percentage must be between 1-100!", text_color="#f1c40f")
                    return

            # 3. Getting users info
            self.app.db_manager.cursor.execute("SELECT id, salary FROM users WHERE username=?", (sender,))
            user_data = self.app.db_manager.cursor.fetchone()
            if not user_data:
                win.destroy()
                return
            u_id, cur_sal = user_data

            # Calculate percent (If it is a certain amount we are turning this to percent)
            percent = val if "Percentage" in raise_type else (val / cur_sal) * 100

            # 4. Remake the salary (Calling SalaryService)
            res = self.app.salary_service.apply_raise(u_id, percent)

            if res:
                # Set the request status to 'Approved'.
                self.app.hr_service.update_request_status(req_id, 'Approved', 'Boss')

                # Send notification
                self.app.notification_service.send(sender,
                                                   f"Your raise is approved! New Salary: {res.new_salary:,.0f} ₺")

                # Refresh the dashboard
                self.load_staff_management()
                self.load_manager_approvals()
                self.update_stat_cards()
                win.destroy()
            else:
                error_lbl.configure(text="❌ Error applying raise in database!", text_color="#e74c3c")

        ctk.CTkButton(win, text="Confirm Raise", command=confirm, fg_color="#2ecc71").pack(pady=15)

    def update_day(self, p_id, new_day_eng):
        """Updates the employee's off-day. Now directly using English values."""

        db_day = new_day_eng

        self.app.db_manager.cursor.execute("SELECT role FROM users WHERE id=?", (p_id,))
        result = self.app.db_manager.cursor.fetchone()
        if not result: return
        u_role = result[0]

        # Boss and Manager can change their off-days without conflict checks
        if u_role in ('Boss', 'Manager'):
            self.app.hr_service.set_off_day_by_id(p_id, db_day)
            self.load_staff_management()
            return

        # Check for staff coverage conflicts before saving
        is_valid, error_msg = self.app.hr_service.check_off_day_conflict(p_id, u_role, db_day)
        if not is_valid:
            pop = ctk.CTkToplevel(self.app)
            pop.title("Conflict Error")
            pop.geometry("300x150")
            pop.attributes("-topmost", True)
            ctk.CTkLabel(pop, text=f"⚠️ {error_msg}", text_color="#e74c3c", font=("Arial", 12, "bold"),
                         wraplength=260).pack(pady=30, padx=20)
            ctk.CTkButton(pop, text="OK", command=pop.destroy, fg_color="#34495e").pack()

            # --- YENİ EKLENEN KISIM: Hata varsa kutunun eski haline dönmesi için listeyi anında yenile! ---
            self.load_staff_management()
            return

        # If valid, save the English day name to the database
        self.app.hr_service.set_off_day_by_id(p_id, db_day)
        self.load_staff_management()

    def change_salary(self, p_id, current_salary, amount):
        new_val = current_salary + amount
        self.app.db_manager.cursor.execute("UPDATE users SET salary=? WHERE id=?", (new_val, p_id))

        percent = (amount / current_salary) * 100 if current_salary != 0 else 0
        date_str = datetime.date.today().isoformat()

        try:
            self.app.db_manager.cursor.execute(
                "INSERT INTO salary_records (user_id, old_salary, new_salary, percent, date) VALUES (?, ?, ?, ?, ?)",
                (p_id, current_salary, new_val, percent, date_str)
            )
        except:
            pass

        self.app.db_manager.conn.commit()

        # --- YENİ EKLENEN BİLDİRİM KISMI ---
        self.app.db_manager.cursor.execute("SELECT username FROM users WHERE id=?", (p_id,))
        result = self.app.db_manager.cursor.fetchone()

        if result:
            target_user = result[0]
            if amount > 0:
                msg = f"Boss made an update to your salary! 📈 Your new salary is: {new_val:,.0f} ₺"
            else:
                msg = f"Boss made a deduction from your salary! 📉 Your new salary is: {new_val:,.0f} ₺"

            self.app.notification_service.send(target_user, msg)
        # -----------------------------------

        self.load_staff_management()
        self.update_stat_cards()

    def open_notice_board(self):
        win = ctk.CTkToplevel(self.app)
        win.title("Notice Board")
        # Filtre sığsın diye pencereyi biraz uzattık (550'den 600'e)
        win.geometry("500x600")
        win.grab_set()

        ctk.CTkLabel(win, text="📝 Global Communication Board", font=("Arial", 18, "bold")).pack(pady=10)

        # --- YENİ EKLENEN FİLTRE ALANI ---
        filter_frame = ctk.CTkFrame(win, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(filter_frame, text="Filter by Target:", font=("Arial", 12, "bold")).pack(side="left", padx=(5, 10))

        roles = ["All", "Manager", "Waiter", "Barista", "Cashier", "Chef", "Cleaner"]

        # Seçim değiştiğinde anında redraw() fonksiyonunu tetikler
        filter_combo = ctk.CTkComboBox(filter_frame, values=roles, width=130, state="readonly",
                                       command=lambda e: redraw())
        filter_combo.set("All")
        filter_combo.pack(side="left")
        # ---------------------------------

        scroll = ctk.CTkScrollableFrame(win, fg_color="#2c3e50")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # args ekledik çünkü Combobox command ile çalışırken parametre gönderir
        def redraw(*args):
            for w in scroll.winfo_children(): w.destroy()
            notes = self.app.note_service.get_notes_for_user(self.user.role)
            selected_filter = filter_combo.get()

            has_notes = False
            for n in notes:
                # Eğer "All" seçili değilse ve mesajın hedefi filtremizle uyuşmuyorsa bu mesajı atla (çizme)
                if selected_filter != "All" and n.target_role != selected_filter:
                    continue

                has_notes = True
                f = ctk.CTkFrame(scroll, fg_color="#34495e", corner_radius=5)
                f.pack(fill="x", pady=5, padx=5)
                head = f"👤 {n.sender_name} ➔ [{n.target_role}] ({n.date})"
                ctk.CTkLabel(f, text=head, font=("Arial", 10, "bold"), text_color="#f1c40f").pack(anchor="w", padx=10)
                ctk.CTkLabel(f, text=n.content, font=("Arial", 12), wraplength=430).pack(anchor="w", padx=10, pady=5)

            if not has_notes:
                ctk.CTkLabel(scroll, text="No notes found for this filter.", text_color="gray").pack(pady=20)

        redraw()

        inf = ctk.CTkFrame(win, fg_color="transparent")
        inf.pack(fill="x", padx=10, pady=10)

        target = ctk.CTkComboBox(inf, values=["Manager", "Waiter", "Barista", "Cashier", "Chef", "Cleaner"], width=110)
        target.pack(side="left", padx=5)

        msg_in = ctk.CTkEntry(inf, placeholder_text="Type here...", width=250)
        msg_in.pack(side="left", padx=5)

        def send():
            if msg_in.get():
                self.app.note_service.add_note(self.user.username, self.user.role, target.get(), msg_in.get())
                msg_in.delete(0, 'end')
                redraw()

        ctk.CTkButton(inf, text="Post", width=70, command=send, fg_color="#2ecc71").pack(side="right")

    def load_shift_reports(self):
        """Refreshes the personnel management and weekly coverage logs with a cleaner UI."""
        # Sekmeyi temizle
        for widget in self.tab_reports.winfo_children():
            widget.destroy()

        # --- SECTION 1: PERSONNEL MANAGEMENT (FIRE STAFF) ---
        ctk.CTkLabel(self.tab_reports, text="🚨 PERSONNEL MANAGEMENT",
                     font=("Arial", 16, "bold"), text_color="#e74c3c").pack(pady=(15, 5))

        sc = ctk.CTkScrollableFrame(self.tab_reports, height=180, border_width=1, border_color="#34495e")
        sc.pack(fill="x", padx=20, pady=5)

        self.app.db_manager.cursor.execute("SELECT id, username, role FROM users WHERE role NOT IN ('Boss','Manager')")
        staff = self.app.db_manager.cursor.fetchall()

        for sid, sname, srole in staff:
            row = ctk.CTkFrame(sc, fg_color="#2c3e50", corner_radius=6)
            row.pack(fill="x", pady=3, padx=5)

            # Sol taraf: İsim ve Rol
            ctk.CTkLabel(row, text=f"👤 {sname.capitalize()}", font=("Arial", 13, "bold"), width=150, anchor="w").pack(
                side="left", padx=15)
            ctk.CTkLabel(row, text=f"[{srole}]", font=("Arial", 11), text_color="gray", width=100).pack(side="left")

            # Sağ taraf: İşten Çıkarma Butonu
            ctk.CTkButton(row, text="Terminate ❌", fg_color="transparent", border_width=1, border_color="#c0392b",
                          hover_color="#c0392b", width=100, height=28,
                          command=lambda i=sid: self.fire_staff(i)).pack(side="right", padx=10, pady=5)

        # --- SECTION 2: WEEKLY COVERAGE TRACKER (DİNAMİK FİLTRE) ---
        ctk.CTkLabel(self.tab_reports, text="📅 WEEKLY COVERAGE TRACKER",
                     font=("Arial", 16, "bold"), text_color="#3498db").pack(pady=(25, 5))

        # Filtre Paneli (Combobox)
        filter_frame = ctk.CTkFrame(self.tab_reports, fg_color="transparent")
        filter_frame.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(filter_frame, text="Select Day:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        import datetime
        current_day = datetime.datetime.now().strftime("%A")

        # Seçim yapıldığında refresh_list fonksiyonunu otomatik çağırır
        day_filter = ctk.CTkComboBox(filter_frame, values=days, width=150, state="readonly",
                                     command=lambda e: refresh_list(e))
        day_filter.set(current_day)  # Varsayılan olarak bugünü gösterir
        day_filter.pack(side="left")

        # Başlık Satırı (Tablo gibi görünmesi için)
        head_frame = ctk.CTkFrame(self.tab_reports, fg_color="transparent")
        head_frame.pack(fill="x", padx=25)

        # "Date" yerine "Role" yaptık çünkü tarih zaten üstten seçiliyor
        ctk.CTkLabel(head_frame, text="Role", font=("Arial", 11, "bold"), text_color="gray", width=120,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(head_frame, text="Employee", font=("Arial", 11, "bold"), text_color="gray", width=150,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(head_frame, text="Status", font=("Arial", 11, "bold"), text_color="gray").pack(side="right",
                                                                                                    padx=20)

        rc = ctk.CTkScrollableFrame(self.tab_reports, border_width=1, border_color="#34495e")
        rc.pack(fill="both", expand=True, padx=20, pady=5)

        def refresh_list(selected_day):
            """Tüm personeli listeler ve seçilen güne göre durumlarını (Present/Absent) belirler"""
            for widget in rc.winfo_children(): widget.destroy()

            # Veritabanından tüm çalışanları off_day bilgisi ile birlikte çek
            self.app.db_manager.cursor.execute(
                "SELECT username, role, off_day FROM users WHERE role NOT IN ('Boss', 'Manager')"
            )
            all_staff = self.app.db_manager.cursor.fetchall()

            if not all_staff:
                ctk.CTkLabel(rc, text="No employees found.", text_color="gray").pack(pady=20)
                return

            for sname, srole, soff_day in all_staff:
                row = ctk.CTkFrame(rc, fg_color="#34495e", corner_radius=4)
                row.pack(fill="x", pady=2, padx=5)

                # Departman/Rol
                ctk.CTkLabel(row, text=f"🏷 {srole}", font=("Arial", 12), width=120, anchor="w").pack(side="left",
                                                                                                     padx=10)

                # Personel Adı
                ctk.CTkLabel(row, text=sname.capitalize(), font=("Arial", 12, "bold"), width=150, anchor="w").pack(
                    side="left")

                # --- YENİ AKILLI DURUM HESAPLAMA ---
                role_count = self.app.hr_service.get_role_count(srole)

                if role_count <= 1:
                    # Departmanda tek kişi varsa mecburen her gün çalışıyor sayılır
                    status_text = "PRESENT (ONLY) ✅"
                    status_color = "#f39c12"  # Turuncu
                elif soff_day == selected_day:
                    status_text = "ABSENT ❌"
                    status_color = "#e74c3c"
                else:
                    status_text = "PRESENT ✅"
                    status_color = "#2ecc71"

                ctk.CTkLabel(row, text=status_text, text_color=status_color, font=("Arial", 11, "bold")).pack(side="right",
                                                                                                              padx=15)

        # İlk açılışta bugünün listesini yükle
        refresh_list(day_filter.get())

    def fire_staff(self, p_id):
        self.app.hr_service.fire_employee(p_id)
        self.load_staff_management()
        self.load_shift_reports()
        self.update_stat_cards()

    def on_tab_change(self):
        if self.tabview.get() == "📊 Performance Tracking":
            self.load_shift_reports()

    def show_cv_popup(self, app_obj):
        win = ctk.CTkToplevel(self.app)
        win.title(f"Detailed CV: {app_obj.cv.name} {app_obj.cv.surname}")
        win.geometry("550x750")  # Deneyimler artabileceği için boyutu biraz büyüttük
        win.grab_set()
        win.attributes("-topmost", True)

        # Ana Başlık
        header_label = ctk.CTkLabel(win, text="📄 CANDIDATE PROFILE", font=("Arial", 22, "bold"), text_color="#3498db")
        header_label.pack(pady=20)

        # Bilgilerin olduğu ana gövde (Frame)
        info_container = ctk.CTkFrame(win, fg_color="transparent")
        info_container.pack(fill="both", expand=False, padx=30)

        # Bilgi Satırı Fonksiyonu
        # Bilgi Satırı Fonksiyonu (Daha temiz görünüm için)
        def create_info_row(parent, label_text, value_text, row_num):
            lbl = ctk.CTkLabel(parent, text=label_text, font=("Arial", 12, "bold"), text_color="gray")
            lbl.grid(row=row_num, column=0, sticky="w", pady=8, padx=10)

            val = ctk.CTkLabel(parent, text=value_text, font=("Arial", 13), text_color="white")
            val.grid(row=row_num, column=1, sticky="w", pady=8, padx=10)

        # 1. Kişisel Bilgiler Bölümü
        create_info_row(info_container, "Full Name:", f"{app_obj.cv.name} {app_obj.cv.surname}", 0)
        create_info_row(info_container, "Gender:", app_obj.cv.gender, 1)
        create_info_row(info_container, "Email:", app_obj.cv.email, 2)
        create_info_row(info_container, "Phone:", app_obj.cv.phone, 3)
        create_info_row(info_container, "Position Applied:", app_obj.desired_role, 4)

        # 2. Deneyim Bölümü Başlığı
        exp_header = ctk.CTkLabel(win, text="🛠 WORK EXPERIENCE", font=("Arial", 14, "bold"), text_color="#f1c40f")
        exp_header.pack(pady=(20, 5), padx=40, anchor="w")

        # 3. DENEYİM VERİSİNİ İŞLEME (Görseldeki hatayı düzelten kısım)
        formatted_exp_text = ""
        raw_data = app_obj.cv.experiences

        if not raw_data or raw_data == "No experience":
            formatted_exp_text = "No work experience provided."
        else:
            try:
                # Veri bazen string içinde string olarak gelebilir, temizliyoruz
                if isinstance(raw_data, str):
                    # Baştaki ve sondaki gereksiz tırnakları temizle
                    clean_data = raw_data.strip('"').replace('\\"', '"')
                    experiences = json.loads(clean_data)
                else:
                    experiences = raw_data

                if not experiences or not isinstance(experiences, list):
                    formatted_exp_text = "No work experience provided."
                else:
                    for i, exp in enumerate(experiences, 1):
                        formatted_exp_text += f"{i}. COMPANY: {exp.get('company', 'N/A').upper()}\n"
                        formatted_exp_text += f"   POSITION: {exp.get('pos', 'N/A')}\n"
                        formatted_exp_text += f"   DATES: {exp.get('date', 'N/A')}\n"
                        formatted_exp_text += "-" * 45 + "\n"

            except Exception as e:
                # Eğer JSON ayrıştırma tamamen başarısız olursa ham veriyi göster ama temizle
                formatted_exp_text = str(raw_data).replace('[', '').replace(']', '').replace('{', '').replace('}', '')

        # Deneyim Kutusu
        exp_box = ctk.CTkTextbox(win, width=480, height=200, corner_radius=10, border_width=1, border_color="#34495e")
        exp_box.pack(pady=5, padx=30)
        exp_box.insert("1.0", formatted_exp_text)
        exp_box.configure(state="disabled")

        # 4. Alt Butonlar (Approve / Reject)
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=30)

        approve_btn = ctk.CTkButton(btn_frame, text="APPROVE & HIRE", fg_color="#2ecc71", hover_color="#27ae60",
                                    width=180, height=40, font=("Arial", 13, "bold"),
                                    command=lambda: [self.process_hire(app_obj.app_id, "Approved"), win.destroy()])
        approve_btn.pack(side="left", padx=15)

        reject_btn = ctk.CTkButton(btn_frame, text="REJECT", fg_color="#e74c3c", hover_color="#c0392b",
                                   width=120, height=40, font=("Arial", 13, "bold"),
                                   command=lambda: [self.process_hire(app_obj.app_id, "Rejected"), win.destroy()])
        reject_btn.pack(side="left", padx=15)