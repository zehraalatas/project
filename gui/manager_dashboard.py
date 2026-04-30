import customtkinter as ctk


class ManagerDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        self.header = ctk.CTkLabel(app, text=f"👔 Müdür Paneli - Hoşgeldin {self.user.username.capitalize()}",
                                   font=("Helvetica", 28, "bold"))
        self.header.pack(pady=(20, 10))

        self.tabview = ctk.CTkTabview(app, width=800, height=450)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        self.tab_requests = self.tabview.add("📨 İç Talepler (İzin/Zam)")
        self.tab_apps = self.tabview.add("👥 Yeni İş Başvuruları")

        self.load_requests()
        self.load_applications()

        self.logout_btn = ctk.CTkButton(app, text="Çıkış Yap", command=self.app.show_login_screen, fg_color="darkred",
                                        width=150)
        self.logout_btn.pack(side="bottom", pady=20)

    def load_requests(self):
        for widget in self.tab_requests.winfo_children(): widget.destroy()
        requests = self.app.hr_service.get_pending_requests()

        scroll = ctk.CTkScrollableFrame(self.tab_requests, width=750, height=350, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for i, req in enumerate(requests, start=1):
            req_id, sender, r_type, detail, status = req

            ctk.CTkLabel(scroll, text=f"Gönderen: {sender.capitalize()} | Tür: {r_type}",
                         font=("Helvetica", 14, "bold"), text_color="#f39c12").grid(row=i, column=0, padx=15, pady=15)

            det_box = ctk.CTkTextbox(scroll, width=250, height=50, wrap="word", fg_color="#2b2b2b")
            det_box.insert("0.0", detail)
            det_box.configure(state="disabled")
            det_box.grid(row=i, column=1, padx=15, pady=15)

            ctk.CTkButton(scroll, text="Onayla ✔", width=80, fg_color="#2ecc71",
                          command=lambda r=req_id, t=r_type, s=sender: self.process_request(r, t, s, "Onaylandı")).grid(
                row=i, column=2, padx=5, pady=15)
            ctk.CTkButton(scroll, text="Reddet ✖", width=80, fg_color="#e74c3c",
                          command=lambda r=req_id, t=r_type, s=sender: self.process_request(r, t, s,
                                                                                            "Reddedildi")).grid(row=i,
                                                                                                                column=3,
                                                                                                                padx=5,
                                                                                                                pady=15)

    def load_applications(self):
        for widget in self.tab_apps.winfo_children(): widget.destroy()
        apps = self.app.hr_service.get_pending_applications()

        scroll = ctk.CTkScrollableFrame(self.tab_apps, width=750, height=350, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for i, app_data in enumerate(apps, start=1):
            app_id, name, role, status = app_data
            ctk.CTkLabel(scroll, text=f"Aday: {name.capitalize()} | İstenen Rol: {role}",
                         font=("Helvetica", 14, "bold")).grid(row=i, column=0, padx=30, pady=15)
            ctk.CTkButton(scroll, text="İşe Al", width=100, fg_color="#2ecc71",
                          command=lambda a=app_id: self.process_app(a, "Onaylandı")).grid(row=i, column=1, padx=10,
                                                                                          pady=15)

    def process_request(self, req_id, r_type, sender, status):
        if r_type == "İzin" and status == "Onaylandı":

            # Kullanıcı bilgilerini al
            self.app.db_manager.cursor.execute(
                "SELECT id, role FROM users WHERE username=?", (sender,)
            )
            result = self.app.db_manager.cursor.fetchone()

            if not result:
                return

            user_id, role = result

            # Tek çalışan kontrolü
            ok, msg = self.app.hr_service.check_off_day_conflict(user_id, role, None)
            # check_off_day_conflict'i biraz güncelleyeceğiz (aşağıda)

            # Müsait gün bul
            available_day = self.app.hr_service.get_available_off_day(user_id, role)

            if not available_day:
                # Hiç müsait gün yok — popup ile bildir
                win = ctk.CTkToplevel(self.app)
                win.title("Uyarı")
                win.geometry("320x160")
                win.grab_set()
                ctk.CTkLabel(win, text=f"⚠️ {sender.capitalize()} için müsait izin günü bulunamadı!\nTüm günler dolu.",
                             font=("Helvetica", 13, "bold"), text_color="#e74c3c", wraplength=280).pack(pady=30)
                ctk.CTkButton(win, text="Tamam", command=win.destroy, width=150, fg_color="#e74c3c").pack()
                return

            # Müsait gün bulundu — onayla ve ata
            win = ctk.CTkToplevel(self.app)
            win.title("İzin Onayı")
            win.geometry("320x200")
            win.grab_set()

            ctk.CTkLabel(win,
                         text=f"✅ {sender.capitalize()} için\notomatik izin günü belirlendi:",
                         font=("Helvetica", 14, "bold")).pack(pady=20)

            ctk.CTkLabel(win, text=f"📅 {available_day}",
                         font=("Helvetica", 22, "bold"), text_color="#2ecc71").pack()

            def confirm():
                self.app.hr_service.set_off_day_by_username(sender, available_day)
                self.app.hr_service.update_request_status(req_id, status)
                self.load_requests()
                win.destroy()

            ctk.CTkButton(win, text="Onayla", command=confirm,
                          fg_color="#2ecc71", width=200, height=40,
                          font=("Helvetica", 13, "bold")).pack(pady=15)

        else:
            self.app.hr_service.update_request_status(req_id, status)
            self.load_requests()

    def process_app(self, app_id, status):
        self.app.hr_service.process_application(app_id, status)
        self.load_applications()