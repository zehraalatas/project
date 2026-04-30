import customtkinter as ctk
import datetime
from models.schedule import Schedule


class EmployeeDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        # Kullanıcının çalışma programını model üzerinden yönetiyoruz
        self.user_schedule = Schedule(self.user.user_id, self.user.off_day)

        # --- Üst Bilgi Paneli ---
        self.header = ctk.CTkLabel(app, text=f"☕ Hoşgeldin {self.user.username.capitalize()}",
                                   font=("Helvetica", 28, "bold"))
        self.header.pack(pady=(30, 10))

        self.role_label = ctk.CTkLabel(app, text=f"Pozisyon: {self.user.role} | Maaş: {self.user.salary} ₺",
                                       font=("Helvetica", 16), text_color="gray")
        self.role_label.pack(pady=5)

        # --- Ana Aksiyon Butonları ---
        # Mesai butonu kaldırıldı, sadece bildirimler kaldı.
        self.notif_btn = ctk.CTkButton(app, text="🔔 Bildirimler", command=self.show_notifications,
                                       width=300, height=40, fg_color="#2c3e50",
                                       font=("Helvetica", 14))
        self.notif_btn.pack(pady=10)

        # --- Otomatik Durum Kaydı (Shifts) ---
        # Bugünün ismini Schedule modelindeki listeye göre alıyoruz
        today_name = self.user_schedule.DAYS[datetime.datetime.today().weekday()]

        # Durumu belirle: Eğer bugün izin günü ise "İzinli", değilse "Çalışıyor"
        current_status = "İzinli" if today_name.lower() == self.user.off_day.lower() else "Çalışıyor"

        # HRService üzerinden sessizce veritabanına log atıyoruz
        self.app.hr_service.log_status(self.user.user_id, self.user.username, current_status)

        # --- Takvim Bölümü ---
        self.schedule_frame = ctk.CTkFrame(app, corner_radius=10)
        self.schedule_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(self.schedule_frame, text="📅 Çalışma Programın", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.table_frame = ctk.CTkFrame(self.schedule_frame, fg_color="transparent")
        self.table_frame.pack(pady=10)

        # Roldeki kişi sayısını kontrol et (İzin kısıtlaması için)
        self.app.db_manager.cursor.execute(
            "SELECT COUNT(*) FROM users WHERE role=?", (self.user.role,)
        )
        role_count = self.app.db_manager.cursor.fetchone()[0]

        # Takvim döngüsü
        for i, day in enumerate(self.user_schedule.DAYS):
            short_day = day[:3]
            ctk.CTkLabel(self.table_frame, text=short_day, font=("Helvetica", 14, "bold"), width=80).grid(
                row=0, column=i, padx=5, pady=5)

            # Mantık: Tek çalışan ise her gün "İzin Yok", değilse OFF kontrolü
            if role_count <= 1:
                status_text = "İzin Yok"
                color = "#7f8c8d"  # Gri (Kilitli/Yetkisiz)
            elif day == self.user.off_day:
                status_text = "OFF"
                color = "#e74c3c"  # Kırmızı (İzinli)
            else:
                status_text = "Çalışıyor"
                color = "#2ecc71"  # Yeşil (Çalışma)

            box = ctk.CTkFrame(self.table_frame, width=80, height=60, fg_color=color, corner_radius=8)
            box.grid(row=1, column=i, padx=5, pady=5)
            box.grid_propagate(False)

            lbl = ctk.CTkLabel(box, text=status_text, font=("Helvetica", 12, "bold"), text_color="white")
            lbl.place(relx=0.5, rely=0.5, anchor="center")

        # --- Talep Butonları ---
        self.btn_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        if role_count <= 1:
            ctk.CTkButton(
                self.btn_frame, text="İzin İste (Kilitli)",
                width=180, height=45, fg_color="gray", state="disabled"
            ).grid(row=0, column=0, padx=10)
        else:
            ctk.CTkButton(self.btn_frame, text="İzin İste", command=lambda: self.open_req("İzin"),
                          width=150, height=45, fg_color="#f39c12").grid(row=0, column=0, padx=10)

        ctk.CTkButton(self.btn_frame, text="Zam İste", command=lambda: self.open_req("Zam"),
                      width=150, height=45, fg_color="#8e44ad").grid(row=0, column=1, padx=10)

        # --- Alt Menü ---
        self.bottom_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", pady=30)

        self.settings_btn = ctk.CTkButton(self.bottom_frame, text="⚙️ Ayarlar", command=self.open_settings,
                                          fg_color="#34495e", hover_color="#2c3e50", width=120)
        self.settings_btn.grid(row=0, column=0, padx=10)

        self.logout_btn = ctk.CTkButton(self.bottom_frame, text="Çıkış Yap", command=self.app.show_login_screen,
                                        fg_color="darkred", width=120)
        self.logout_btn.grid(row=0, column=1, padx=10)

        self.refresh_notif_badge()

    # Bildirim metotları ve ayarlar metotları aynı kalıyor...
    def refresh_notif_badge(self):
        unread = self.app.notification_service.get_unread(self.user.username)
        if len(unread) > 0:
            self.notif_btn.configure(text=f"🔔 Bildirimler ({len(unread)})", fg_color="#e67e22")
        else:
            self.notif_btn.configure(text="🔔 Bildirimler", fg_color="#2c3e50")

    def show_notifications(self):
        unread = self.app.notification_service.get_unread(self.user.username)
        win = ctk.CTkToplevel(self.app)
        win.title("Bildirimler")
        win.geometry("350x300")
        win.grab_set()

        if not unread:
            ctk.CTkLabel(win, text="Okunmamış bildirim yok 📭", font=("Helvetica", 14), text_color="gray").pack(pady=40)
        else:
            for notif in unread:
                ctk.CTkLabel(win, text=f"• {notif.message}", font=("Helvetica", 13), wraplength=300).pack(pady=8,
                                                                                                          padx=20)

            def mark_read():
                self.app.notification_service.mark_all_read(self.user.username)
                self.refresh_notif_badge()
                win.destroy()

            ctk.CTkButton(win, text="Tümünü Okundu İşaretle", command=mark_read, fg_color="#3498db").pack(pady=15)

    def open_req(self, req_type):
        win = ctk.CTkToplevel(self.app)
        win.title(f"{req_type} Talebi")
        win.geometry("300x200")
        win.grab_set()
        detail_entry = ctk.CTkEntry(win, placeholder_text="Açıklama...", width=250)
        detail_entry.pack(pady=20)

        def submit():
            self.app.hr_service.submit_internal_request(self.user.username, req_type, detail_entry.get())
            win.destroy()

        ctk.CTkButton(win, text="Gönder", command=submit).pack(pady=10)

    def open_settings(self):
        # Ayarlar penceresini oluştur
        win = ctk.CTkToplevel(self.app)
        win.title("Hesap Ayarları")
        win.geometry("350x400")
        win.grab_set() # Pencere kapanmadan ana ekrana dokunulmasın

        ctk.CTkLabel(win, text="⚙️ Bilgileri Güncelle", font=("Helvetica", 18, "bold")).pack(pady=20)

        # Mevcut kullanıcı adını otomatik doldur
        user_entry = ctk.CTkEntry(win, placeholder_text="Yeni Kullanıcı Adı", width=250, height=40)
        user_entry.insert(0, self.user.username)
        user_entry.pack(pady=10)

        # Şifre alanı
        pass_entry = ctk.CTkEntry(win, placeholder_text="Yeni Şifre", show="*", width=250, height=40)
        pass_entry.pack(pady=10)

        # Uyarı/Başarı mesajı etiketi
        status_lbl = ctk.CTkLabel(win, text="", font=("Helvetica", 12, "bold"))
        status_lbl.pack(pady=5)

        def save_settings():
            new_user = user_entry.get().strip()
            new_pass = pass_entry.get().strip()

            # Boş alan kontrolü
            if not new_user or not new_pass:
                status_lbl.configure(text="Alanlar boş bırakılamaz!", text_color="#e74c3c")
                return

            # AuthService üzerinden validation ve kayıt işlemini başlat
            # Artık AuthService içindeki validator (en az 3 karakter kullanıcı adı, 6 karakter şifre) kuralları geçerli.
            success, msg = self.app.auth_service.update_credentials(self.user.user_id, new_user, new_pass)

            if success:
                status_lbl.configure(text=msg, text_color="#2ecc71")
                # Localdeki kullanıcı adını ve başlığı anlık güncelle
                self.user.username = new_user
                self.header.configure(text=f"☕ Hoşgeldin {new_user.capitalize()}")
                win.after(1500, win.destroy) # 1.5 saniye sonra pencereyi kapat
            else:
                status_lbl.configure(text=msg, text_color="#e74c3c")

        ctk.CTkButton(win, text="Kaydet", command=save_settings,
                      fg_color="#3498db", width=200, height=40).pack(pady=15)