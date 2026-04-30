import customtkinter as ctk
from models.application import JobApplication
from models.leave_request import LeaveRequest
from models.raise_request import RaiseRequest

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

        self.app.db_manager.cursor.execute(
            "SELECT id, sender_name, request_type, detail, status FROM requests WHERE status='Bekliyor'")
        rows = self.app.db_manager.cursor.fetchall()

        # Talepleri tipine göre sınıflara ayırıyoruz
        requests = []
        for r in rows:
            if r[2] == "İzin":
                requests.append(LeaveRequest(r[0], r[1], r[3], r[4]))
            else:
                requests.append(RaiseRequest(r[0], r[1], r[3], r[4]))

        scroll = ctk.CTkScrollableFrame(self.tab_requests, width=750, height=350, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for i, req_obj in enumerate(requests, start=1):
            # req_obj artık bir nesne (Object)
            color = "#f39c12" if isinstance(req_obj, LeaveRequest) else "#8e44ad"

            ctk.CTkLabel(scroll, text=f"Gönderen: {req_obj.sender.capitalize()} | Tür: {req_obj.request_type}",
                         font=("Helvetica", 14, "bold"), text_color=color).grid(row=i, column=0, padx=15, pady=15)

            det_box = ctk.CTkTextbox(scroll, width=250, height=50, wrap="word")
            det_box.insert("0.0", req_obj.detail)
            det_box.configure(state="disabled")
            det_box.grid(row=i, column=1, padx=15, pady=15)

            # İşlemler aynı kalabilir ama arka planda nesneyle çalıştık
            ctk.CTkButton(scroll, text="Onayla ✔", width=80, fg_color="#2ecc71",
                          command=lambda r=req_obj.request_id, t=req_obj.request_type, s=req_obj.sender:
                          self.process_request(r, t, s, "Onaylandı")).grid(row=i, column=2, padx=5, pady=15)

    def load_applications(self):
        for widget in self.tab_apps.winfo_children(): widget.destroy()

        # Ham veriyi çek
        self.app.db_manager.cursor.execute(
            "SELECT id, name, desired_role, status FROM applications WHERE status='Bekliyor'")
        rows = self.app.db_manager.cursor.fetchall()

        # Ham veriyi nesnelere (Object) dönüştür
        apps = [JobApplication(r[0], r[1], r[2], r[3]) for r in rows]

        scroll = ctk.CTkScrollableFrame(self.tab_apps, width=750, height=350, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for i, app_obj in enumerate(apps, start=1):
            # r[1] yerine artık app_obj.name kullanabiliyoruz
            ctk.CTkLabel(scroll, text=f"Aday: {app_obj.name.capitalize()} | İstenen Rol: {app_obj.desired_role}",
                         font=("Helvetica", 14, "bold")).grid(row=i, column=0, padx=30, pady=15)

            ctk.CTkButton(scroll, text="İşe Al", width=100, fg_color="#2ecc71",
                          command=lambda a=app_obj.app_id: self.process_app(a, "Onaylandı")).grid(row=i, column=1,
                                                                                                  padx=10, pady=15)

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
                self.app.notification_service.send(sender, "İzin talebiniz onaylandı ✅")
                self.load_requests()
                win.destroy()

            ctk.CTkButton(win, text="Onayla", command=confirm,
                          fg_color="#2ecc71", width=200, height=40,
                          font=("Helvetica", 13, "bold")).pack(pady=15)



        # else bloğunu şöyle güncellemeyi dene:

        else:

            self.app.hr_service.update_request_status(req_id, status)

            if status == "Onaylandı":

                self.app.notification_service.send(sender, f"{r_type} talebiniz onaylandı ✅")

            elif status == "Reddedildi":

                self.app.notification_service.send(sender, f"{r_type} talebiniz reddedildi ❌")

            self.load_requests()
    def process_app(self, app_id, status):
        self.app.hr_service.process_application(app_id, status)
        self.load_applications()