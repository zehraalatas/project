import customtkinter as ctk
import datetime


class EmployeeDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        self.header = ctk.CTkLabel(app, text=f"☕ Hoşgeldin {self.user.username.capitalize()}",
                                   font=("Helvetica", 28, "bold"))
        self.header.pack(pady=(30, 10))

        self.role_label = ctk.CTkLabel(app, text=f"Pozisyon: {self.user.role} | Maaş: {self.user.salary} ₺",
                                       font=("Helvetica", 16), text_color="gray")
        self.role_label.pack(pady=5)

        self.shift_btn = ctk.CTkButton(app, text="🟢 Mesai Yap", command=self.do_shift, width=300, height=50,
                                       font=("Helvetica", 18, "bold"), fg_color="#2ecc71")
        self.shift_btn.pack(pady=20)

        self.schedule_frame = ctk.CTkFrame(app, corner_radius=10)
        self.schedule_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(self.schedule_frame, text="📅 Çalışma Programın", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.table_frame = ctk.CTkFrame(self.schedule_frame, fg_color="transparent")
        self.table_frame.pack(pady=10)

        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        self.day_boxes = {}
        self.day_labels = {}

        for i, day in enumerate(self.days):
            short_day = day[:3]
            ctk.CTkLabel(self.table_frame, text=short_day, font=("Helvetica", 14, "bold"), width=80).grid(row=0,
                                                                                                          column=i,
                                                                                                          padx=5,
                                                                                                          pady=5)

            if day == self.user.off_day:
                status_text = "OFF"
                color = "#e74c3c"
            else:
                status_text = "09:00\n17:00"
                color = "#2980b9"

            box = ctk.CTkFrame(self.table_frame, width=80, height=60, fg_color=color, corner_radius=8)
            box.grid(row=1, column=i, padx=5, pady=5)
            box.grid_propagate(False)

            lbl = ctk.CTkLabel(box, text=status_text, font=("Helvetica", 12, "bold"), text_color="white")
            lbl.place(relx=0.5, rely=0.5, anchor="center")

            self.day_boxes[day] = box
            self.day_labels[day] = lbl

        self.btn_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        ctk.CTkButton(self.btn_frame, text="İzin İste", command=lambda: self.open_req("İzin"), width=150, height=45,
                      fg_color="#f39c12").grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.btn_frame, text="Zam İste", command=lambda: self.open_req("Zam"), width=150, height=45,
                      fg_color="#8e44ad").grid(row=0, column=1, padx=10)

        # ALT BUTONLAR (AYARLAR VE ÇIKIŞ YAN YANA)
        self.bottom_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", pady=30)

        self.settings_btn = ctk.CTkButton(self.bottom_frame, text="⚙️ Ayarlar", command=self.open_settings,
                                          fg_color="#34495e", hover_color="#2c3e50", width=120)
        self.settings_btn.grid(row=0, column=0, padx=10)

        self.logout_btn = ctk.CTkButton(self.bottom_frame, text="Çıkış Yap", command=self.app.show_login_screen,
                                        fg_color="darkred", width=120)
        self.logout_btn.grid(row=0, column=1, padx=10)

    def do_shift(self):
        today_index = datetime.datetime.today().weekday()
        today_str = self.days[today_index]

        if today_str == self.user.off_day:
            self.shift_btn.configure(text="Bugün Tatilsin!", fg_color="#e74c3c", state="disabled")
        else:
            self.day_boxes[today_str].configure(fg_color="#27ae60")
            self.day_labels[today_str].configure(text="Bitti ✔")
            self.shift_btn.configure(text="Mesai Tamamlandı", state="disabled", fg_color="gray")

    def open_req(self, req_type):
        win = ctk.CTkToplevel(self.app)
        win.title(f"{req_type} Talebi")
        win.geometry("300x200")
        win.grab_set()

        detail_entry = ctk.CTkEntry(win, placeholder_text="Kısaca açıklayın...", width=250)
        detail_entry.pack(pady=20)

        def submit():
            self.app.hr_service.submit_internal_request(self.user.username, req_type, detail_entry.get())
            win.destroy()

        ctk.CTkButton(win, text="Gönder", command=submit).pack(pady=10)

    # YENİ: Ayarlar Penceresi
    def open_settings(self):
        win = ctk.CTkToplevel(self.app)
        win.title("Hesap Ayarları")
        win.geometry("350x350")
        win.grab_set()

        ctk.CTkLabel(win, text="⚙️ Bilgileri Güncelle", font=("Helvetica", 18, "bold")).pack(pady=20)

        user_entry = ctk.CTkEntry(win, placeholder_text="Yeni Kullanıcı Adı", width=250, height=40)
        user_entry.insert(0, self.user.username)  # Mevcut ismi otomatik doldur
        user_entry.pack(pady=10)

        pass_entry = ctk.CTkEntry(win, placeholder_text="Yeni Şifre", show="*", width=250, height=40)
        pass_entry.pack(pady=10)

        status_lbl = ctk.CTkLabel(win, text="", font=("Helvetica", 12, "bold"))
        status_lbl.pack(pady=5)

        def save_settings():
            new_user = user_entry.get().strip()
            new_pass = pass_entry.get().strip()

            if not new_user or not new_pass:
                status_lbl.configure(text="Alanlar boş bırakılamaz!", text_color="#e74c3c")
                return

            # Veritabanını güncelle
            success, msg = self.app.auth_service.update_credentials(self.user.user_id, new_user, new_pass)

            if success:
                status_lbl.configure(text=msg, text_color="#2ecc71")
                self.user.username = new_user  # Kendi ekranındaki ismi anında değiştir
                self.header.configure(text=f"☕ Hoşgeldin {new_user.capitalize()}")

                # 1.5 saniye sonra pencereyi otomatik kapat
                win.after(1500, win.destroy)
            else:
                status_lbl.configure(text=msg, text_color="#e74c3c")

        ctk.CTkButton(win, text="Kaydet", command=save_settings, fg_color="#3498db", width=200, height=40).pack(pady=15)