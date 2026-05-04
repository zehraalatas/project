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

        # Sekmeleri Oluştur
        self.tabview = ctk.CTkTabview(app, width=800, height=450)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        # Eski satırı bul ve şununla değiştir:
        self.tab_my_schedule = self.tabview.add("👤 Profil ")
        self.tab_requests = self.tabview.add("📨 İç Talepler (İzin/Zam)")


        # Verileri Yükle
        self.load_requests()
        self.load_my_schedule()

        self.logout_btn = ctk.CTkButton(app, text="Çıkış Yap", command=self.app.show_login_screen, fg_color="darkred",
                                        width=150)
        self.logout_btn.pack(side="bottom", pady=20)

    def load_requests(self):
        for widget in self.tab_requests.winfo_children(): widget.destroy()

        # Sadece "Müdür Onayı Bekliyor" statüsündeki İzin ve Zam taleplerini çek
        self.app.db_manager.cursor.execute(
            "SELECT id, sender_name, request_type, detail, status FROM requests WHERE status='Müdür Onayı Bekliyor'"
        )
        requests = self.app.db_manager.cursor.fetchall()

        if not requests:
            ctk.CTkLabel(self.tab_requests, text="Bekleyen personel talebi yok.",
                         font=("Helvetica", 14), text_color="gray").pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.tab_requests, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for req in requests:
            r_id, sender, r_type, detail, status = req
            frame = ctk.CTkFrame(scroll)
            frame.pack(pady=5, padx=20, fill="x")

            # Görsel ikonlar ekleyelim
            icon = "📅" if r_type == "İzin" else "💰"

            ctk.CTkLabel(frame, text=f"{icon} {sender.capitalize()} - {r_type} ({detail})",
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)

            # Butonlar: Onaylarsa Patron'a düşer, Redderse kapanır.
            ctk.CTkButton(frame, text="Patrona İlet ✅", width=120, fg_color="#3498db",
                          command=lambda r=r_id, s=sender: self.process_request(r, "Onaylandı", s)).pack(side="right",
                                                                                                         padx=10)

            ctk.CTkButton(frame, text="Reddet ❌", width=100, fg_color="#e74c3c",
                          command=lambda r=r_id, s=sender: self.process_request(r, "Reddedildi", s)).pack(side="right",
                                                                                                          padx=10)

    def process_request(self, req_id, status, sender):
        # HRService içindeki mantığı 'Müdür' rolüyle çağırıyoruz
        res = self.app.hr_service.update_request_status(req_id, status, "Müdür")

        if res:
            # İşlem başarılıysa bildirim gönder
            if status == "Onaylandı":
                self.app.notification_service.send(sender,
                                                   "Talebiniz Müdür tarafından onaylandı, Patron onayı bekleniyor. ⏳")
            else:
                self.app.notification_service.send(sender, "Talebiniz Müdür tarafından reddedildi. ❌")

        # Ekranı tazele
        self.load_requests()

    def load_my_schedule(self):
        for widget in self.tab_my_schedule.winfo_children(): widget.destroy()

        # 1. Kullanıcı bilgilerini çek
        self.app.db_manager.cursor.execute("SELECT role, salary, off_day FROM users WHERE username=?", (self.user.username,))
        result = self.app.db_manager.cursor.fetchone()
        role, salary, off_day = result if result else ("Müdür", 0, "Belirsiz")

        # 2. Üst Bilgi (Pozisyon ve Maaş - Resimdeki gibi gri ve ortalanmış)
        info_label = ctk.CTkLabel(self.tab_my_schedule, text=f"Pozisyon: {role} | Maaş: {salary:,.1f} ₺", font=("Helvetica", 16), text_color="gray")
        info_label.pack(pady=(10, 20))

        # 3. Bildirimler Butonu (Resimdeki geniş, koyu mavi buton)
        notif_btn = ctk.CTkButton(self.tab_my_schedule, text="🔔 Bildirimler", fg_color="#34495e", hover_color="#2c3e50", width=400, height=40)
        notif_btn.pack(pady=10)

        self.board_btn = ctk.CTkButton(self.tab_my_schedule, text="📝 Tüm Departmanların Panosu",
                                       command=self.open_notice_board, fg_color="#8e44ad",
                                       hover_color="#732d91", width=400, height=40)
        self.board_btn.pack(pady=10)

        # 4. Çalışma Programı Başlığı
        schedule_label = ctk.CTkLabel(self.tab_my_schedule, text="📅 Çalışma Programın", font=("Helvetica", 18, "bold"))
        schedule_label.pack(pady=(30, 20))

        # 5. Günler Kutucukları (İşte resimdeki o yan yana diziliş)
        days_frame = ctk.CTkFrame(self.tab_my_schedule, fg_color="transparent")
        days_frame.pack(pady=10)

        gunler_kisa = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cts", "Paz"]
        gunler_uzun = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        for i in range(7):
            day_col = ctk.CTkFrame(days_frame, fg_color="transparent")
            day_col.grid(row=0, column=i, padx=10)

            # Üstteki gün ismi
            ctk.CTkLabel(day_col, text=gunler_kisa[i], font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

            # Alttaki renkli kutu (İzin gününe denk geliyorsa kırmızı OFF, değilse yeşil Çalışıyor)
            is_off = (gunler_uzun[i] == off_day)
            box_color = "#e74c3c" if is_off else "#2ecc71"
            box_text = "OFF" if is_off else "Çalışıyor"

            box = ctk.CTkFrame(day_col, fg_color=box_color, width=90, height=80, corner_radius=10)
            box.pack_propagate(False) # Çerçevenin içindeki yazıya göre küçülmesini engeller, boyutunu sabit tutar
            box.pack()

            ctk.CTkLabel(box, text=box_text, font=("Helvetica", 14, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # 6. Alt Butonlar (İzin İste ve Zam İste)
        btn_frame = ctk.CTkFrame(self.tab_my_schedule, fg_color="transparent")
        btn_frame.pack(pady=40)

        # Turuncu/Sarı İzin Butonu
        izin_btn = ctk.CTkButton(btn_frame, text="İzin İste", fg_color="#f39c12", hover_color="#d68910",
                                 width=160, height=45, font=("Helvetica", 14, "bold"), command=self.open_leave_popup)
        izin_btn.pack(side="left", padx=20)

        # Mor Zam Butonu
        zam_btn = ctk.CTkButton(btn_frame, text="Zam İste", fg_color="#8e44ad", hover_color="#732d91",
                                width=160, height=45, font=("Helvetica", 14, "bold"), command=self.open_raise_popup)
        zam_btn.pack(side="left", padx=20)


    # --- YENİ EKLENEN POPUP FONKSİYONLARI ---
    # (Butonlara basılınca giriş alanını sayfa içinde değil, tatlı bir pencere olarak açar)

    def open_leave_popup(self):
        # Özel bir küçük pencere (Toplevel) oluşturuyoruz
        popup = ctk.CTkToplevel(self.app)
        popup.title("İzin Talebi")
        popup.geometry("300x200")
        popup.grab_set() # Kullanıcının sadece bu pencereye odaklanmasını sağlar
        popup.attributes("-topmost", True) # Pencereyi en üstte tutar

        ctk.CTkLabel(popup, text="Hangi gün için izin istiyorsunuz?", font=("Helvetica", 14, "bold")).pack(pady=(25, 10))

        # Günlerin listesi
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        combo = ctk.CTkComboBox(popup, values=days, width=180, state="readonly") # Sadece listeden seçilebilir
        combo.set("Gün Seçiniz")
        combo.pack(pady=10)

        # Onay Butonunun İşlevi
        def submit():
            secilen_gun = combo.get()
            if secilen_gun != "Gün Seçiniz":
                self.send_manager_request("İzin", secilen_gun)
                popup.destroy() # Talebi gönderip pencereyi kapatır

        ctk.CTkButton(popup, text="Talebi Gönder", fg_color="#f39c12", hover_color="#d68910", font=("Helvetica", 13, "bold"), command=submit).pack(pady=15)
    def open_raise_popup(self):
        dialog = ctk.CTkInputDialog(text="Zam talebinizi giriniz:\n(Örn: %15 veya 5000 TL)", title="Zam Talebi")
        istek = dialog.get_input()
        if istek:
            self.send_manager_request("Zam", istek)

    def send_manager_request(self, req_type, detail):
        self.app.hr_service.submit_manager_request(self.user.username, req_type, detail)
        self.app.notification_service.send(self.user.username, f"✅ {req_type} talebiniz değerlendirilmesi için Patron'a iletildi!")
        print(f"Başarılı: {req_type} talebi ({detail}) patrona iletildi.")
        print(f"Başarılı: {req_type} talebi ({detail}) patrona iletildi.")

    def open_notice_board(self):
        win = ctk.CTkToplevel(self.app)
        win.title("Genel Pano (Yönetici)")
        win.geometry("500x550")
        win.grab_set()

        ctk.CTkLabel(win, text="📝 Tüm Departmanların İletişim Panosu", font=("Helvetica", 18, "bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(win, fg_color="#2c3e50")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def load_notes():
            for w in scroll.winfo_children(): w.destroy()
            notes = self.app.note_service.get_notes_for_user(self.user.role)
            if not notes:
                ctk.CTkLabel(scroll, text="Henüz bir not yok.", text_color="gray").pack(pady=20)
            for note in notes:
                msg_frame = ctk.CTkFrame(scroll, fg_color="#34495e", corner_radius=8)
                msg_frame.pack(fill="x", pady=5, padx=5)
                # Yöneticilere özel: Mesajın kime gittiğini (Hedef) de gösteriyoruz
                header_text = f"👤 {note.sender_name} ➔ [Hedef: {note.target_role}] ({note.date})"
                ctk.CTkLabel(msg_frame, text=header_text, font=("Helvetica", 11, "bold"), text_color="#f1c40f",
                             anchor="w").pack(fill="x", padx=10, pady=(5, 0))
                ctk.CTkLabel(msg_frame, text=note.content, font=("Helvetica", 13), anchor="w", wraplength=430).pack(
                    fill="x", padx=10, pady=(0, 5))

        load_notes()

        input_frame = ctk.CTkFrame(win, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)

        # Yöneticiler mesaj atarken hedef departmanı seçsin
        target_combo = ctk.CTkComboBox(input_frame, values=["Garson", "Barista", "Kasiyer", "Aşçı", "Temizlikçi"],
                                       width=110)
        target_combo.pack(side="left", padx=5)

        msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Not yazın...", width=250)
        msg_entry.pack(side="left", padx=5)

        def send_note():
            content = msg_entry.get().strip()
            target = target_combo.get()
            if content:
                self.app.note_service.add_note(self.user.username, self.user.role, target, content)
                msg_entry.delete(0, 'end')
                load_notes()

        ctk.CTkButton(input_frame, text="Gönder", width=70, command=send_note, fg_color="#2ecc71").pack(side="right",
                                                                                                        padx=5)