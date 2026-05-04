import customtkinter as ctk

import customtkinter as ctk


class PatronDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        # 1. Kartların içinde duracağı ana çerçeve
        self.stat_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.stat_frame.pack(pady=20, padx=20, fill="x")  # Ekranda görünmesini sağlayan satır bu!

        # 2. İstatistik kartlarını veritabanından çekip oluştur
        self.update_stat_cards()

        self.tabview = ctk.CTkTabview(app)
        self.tabview.pack(pady=5, padx=20, fill="both", expand=True)

        # Sekmeleri sadeleştirdik ve birleştirdik
        self.tab_staff_manage = self.tabview.add("👥 Personel ve Maaş Yönetimi")
        self.tab_approvals = self.tabview.add("📩 Müdür Onayları")
        self.tab_applications = self.tabview.add("👥 İş Başvuruları")
        self.tabview.add("📊 Personel Takip")
        self.tab_reports = self.tabview.tab("📊 Personel Takip")

        # Verileri Yükle
        self.load_staff_management()
        self.load_manager_approvals()
        self.load_job_applications()

        # Sekme değiştiğinde çalışacak fonksiyon
        self.tabview.configure(command=self.on_tab_change)

        self.board_btn = ctk.CTkButton(app, text="📝 Şirket Genel Panosu", command=self.open_notice_board,
                                       fg_color="#8e44ad", width=200)
        self.board_btn.pack(side="bottom", pady=(5, 10))

        self.logout_btn = ctk.CTkButton(app, text="Güvenli Çıkış", command=self.app.show_login_screen,
                                        fg_color="darkred")
        self.logout_btn.pack(side="bottom", pady=10)


    def update_stat_cards(self):
        # Önce mevcut kartları temizle
        for widget in self.stat_frame.winfo_children():
            widget.destroy()

        # ReportService üzerinden güncel verileri çek
        aktif_personel = self.app.report_service.get_active_employee_count()
        toplam_maas = self.app.report_service.get_total_salary_cost()

        # Kartları oluştur (Kasa verisi şimdilik sabit, diğerleri dinamik)
        self.create_stat_card(self.stat_frame, "Günlük Kasa", "14.250 ₺", "#2ecc71", 0)
        self.create_stat_card(self.stat_frame, "Maaş Gideri", f"{toplam_maas:,.0f} ₺", "#e74c3c", 1)
        self.create_stat_card(self.stat_frame, "Aktif Çalışan", f"{aktif_personel}", "#f1c40f", 2)

    def create_stat_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, border_width=2, border_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)  # Kartların eşit dağılmasını sağlar

        ctk.CTkLabel(card, text=title, font=("Helvetica", 14, "bold"), text_color="gray").pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=("Helvetica", 22, "bold"), text_color=color).pack(pady=(0, 10))

    def load_staff_management(self):
        for widget in self.tab_staff_manage.winfo_children(): widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_staff_manage, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        # Patron hariç tüm personeli çek
        self.app.db_manager.cursor.execute(
            "SELECT id, username, role, salary, off_day FROM users WHERE role != 'Patron'")
        staff = self.app.db_manager.cursor.fetchall()

        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        for i, person in enumerate(staff):
            p_id, name, role, salary, current_off = person

            frame = ctk.CTkFrame(scroll, corner_radius=8, border_width=1, border_color="#34495e")
            frame.pack(fill="x", pady=4, padx=5)

            # 1. Sütun: Personel İsmi ve Pozisyonu
            ctk.CTkLabel(frame, text=f"👤 {name.capitalize()} ({role})", font=("Helvetica", 14, "bold"), width=150,
                         anchor="w").pack(side="left", padx=10, pady=10)

            # 2. Sütun: Maaş
            ctk.CTkLabel(frame, text=f"{salary:,.0f} ₺", font=("Helvetica", 14, "bold"), text_color="#2ecc71", width=80,
                         anchor="e").pack(side="left", padx=5)

            # Standart Hızlı Butonlar (1000 TL)
            ctk.CTkButton(frame, text="+1k", width=40, fg_color="#27ae60", hover_color="#2ecc71",
                          command=lambda id=p_id, s=salary: self.change_salary(id, s, 1000)).pack(side="left", padx=2)
            ctk.CTkButton(frame, text="-1k", width=40, fg_color="#d35400", hover_color="#e67e22",
                          command=lambda id=p_id, s=salary: self.change_salary(id, s, -1000)).pack(side="left", padx=2)

            # Özel Tutar Girişi ve Özel +/- Butonları
            custom_amount = ctk.CTkEntry(frame, width=70, placeholder_text="Miktar")
            custom_amount.pack(side="left", padx=(15, 2))

            ctk.CTkButton(frame, text="+", width=30, fg_color="#2ecc71",
                          command=lambda id=p_id, s=salary, e=custom_amount: self.apply_custom_salary(id, s, e.get(),
                                                                                                      1)).pack(
                side="left", padx=2)
            ctk.CTkButton(frame, text="-", width=30, fg_color="#e74c3c",
                          command=lambda id=p_id, s=salary, e=custom_amount: self.apply_custom_salary(id, s, e.get(),
                                                                                                      -1)).pack(
                side="left", padx=2)

            # 3. Sütun: İzin Günü Ayarlama (Artık en sağda sadece bu var)
            combo = ctk.CTkComboBox(frame, values=days, width=110)
            combo.set(current_off)
            combo.pack(side="left", padx=(25, 5))

            ctk.CTkButton(frame, text="Kaydet", width=80, fg_color="#3498db",
                          command=lambda id=p_id, c=combo: self.update_day(id, c.get())).pack(side="left", padx=5)
    def apply_custom_salary(self, p_id, current_salary, amount_str, multiplier):
        """Özel girilen miktarı kontrol eder ve change_salary'ye paslar"""
        # Kullanıcı boş bırakırsa veya harf girerse uyar
        if not amount_str.replace('.', '', 1).isdigit():
            win = ctk.CTkToplevel(self.app)
            win.title("Hata")
            win.geometry("250x120")
            win.grab_set()
            ctk.CTkLabel(win, text="⚠️ Lütfen sayı girin!", text_color="#e74c3c", font=("Helvetica", 14, "bold")).pack(
                pady=30)
            ctk.CTkButton(win, text="Tamam", command=win.destroy, width=100, fg_color="#e74c3c").pack()
            return

        # multiplier 1 ise toplar, -1 ise çıkarır
        amount = float(amount_str) * multiplier

        # Mevcut fonksiyonumuzu kullanarak işlemi veritabanına kaydettiriyoruz
        self.change_salary(p_id, current_salary, amount)

    def load_manager_approvals(self):
        for widget in self.tab_approvals.winfo_children():
            widget.destroy()

        self.app.db_manager.cursor.execute("SELECT * FROM requests WHERE status='Patron Onayı Bekliyor'")
        requests = self.app.db_manager.cursor.fetchall()

        if not requests:
            ctk.CTkLabel(self.tab_approvals, text="Bekleyen onay yok.", font=("Helvetica", 14), text_color="gray").pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.tab_approvals, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for req in requests:
            r_id, sender, r_type, detail, status = req
            frame = ctk.CTkFrame(scroll)
            frame.pack(pady=5, padx=20, fill="x")

            ctk.CTkLabel(frame, text=f"👤 {sender.capitalize()} - {r_type} ({detail})",
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)

            if r_type == "Zam":
                ctk.CTkButton(frame, text="Oran Belirle", width=120, fg_color="#2ecc71",
                              command=lambda r=r_id, s=sender: self.open_raise_popup(r, s)).pack(side="right", padx=10)
            else:
                # DEĞİŞİKLİK BURADA: Artık butona basıldığında r_type (İzin) ve detail (Gün adı) bilgilerini de yolluyoruz
                ctk.CTkButton(frame, text="Kesin Onay", width=120, fg_color="#3498db",
                              command=lambda r=r_id, s=sender, rt=r_type, d=detail: self.final_confirm(r, s, rt, d)).pack(side="right", padx=10)

    def final_confirm(self, req_id, sender, r_type, detail):
        # 1. Talebin statüsünü "Onaylandı" yap
        self.app.hr_service.update_request_status(req_id, "Onaylandı", "Patron")

        # 2. EĞER TALEP "İZİN" İSE, KİŞİNİN İZİN GÜNÜNÜ OTOMATİK DEĞİŞTİR
        if r_type == "İzin":
            self.app.hr_service.set_off_day_by_username(sender, detail)
            bildirim_mesaji = f"İzin talebiniz ({detail}) Patron tarafından kesin onaylandı! ✅"
        else:
            bildirim_mesaji = "Talebiniz Patron tarafından kesin onaylandı! ✅"

        # 3. Ekranları tazele (Personel sekmesindeki güncellenmiş izin gününü görmek için)
        self.load_manager_approvals()
        self.load_staff_management()

        # 4. Personele bildirim gönder
        self.app.notification_service.send(sender, bildirim_mesaji)
    def load_job_applications(self):
        for widget in self.tab_applications.winfo_children():
            widget.destroy()

        # HRService üzerinden bekleyen başvuruları çek
        apps = self.app.hr_service.get_pending_applications()

        scroll = ctk.CTkScrollableFrame(self.tab_applications, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for i, app_data in enumerate(apps):
            # app_data: (id, name, role, status)
            app_id, name, role, status = app_data

            frame = ctk.CTkFrame(scroll)
            frame.pack(pady=5, padx=20, fill="x")

            ctk.CTkLabel(frame, text=f"👤 {name.capitalize()} - {role}",
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)

            # Onay Butonu
            ctk.CTkButton(frame, text="İşe Al ✅", width=100, fg_color="#2ecc71",
                          command=lambda a=app_id: self.process_hire(a, "Onaylandı")).pack(side="right", padx=10)

            # Red Butonu
            ctk.CTkButton(frame, text="Reddet ❌", width=100, fg_color="#e74c3c",
                          command=lambda a=app_id: self.process_hire(a, "Reddedildi")).pack(side="right", padx=10)

    def process_hire(self, app_id, status):
        self.app.hr_service.process_application(app_id, status)
        self.load_job_applications()
        self.update_stat_cards()  # İstatistikleri (aktif çalışan sayısı) tazele

    def open_raise_popup(self, req_id, sender):
        win = ctk.CTkToplevel(self.app)
        win.title("Zam Miktarı Belirle")
        win.geometry("350x260")
        win.grab_set()
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=f"💰 {sender.capitalize()} için zam belirle", font=("Helvetica", 15, "bold")).pack(
            pady=(20, 10))

        # Seçim: Yüzde mi, Net Tutar mı?
        type_var = ctk.StringVar(value="Net Tutar (₺)")
        combo_type = ctk.CTkComboBox(win, values=["Net Tutar (₺)", "Yüzde (%)"], variable=type_var, width=160,
                                     state="readonly")
        combo_type.pack(pady=5)

        # Giriş Alanı
        entry = ctk.CTkEntry(win, placeholder_text="Miktarı girin...", width=160)
        entry.pack(pady=10)

        status_lbl = ctk.CTkLabel(win, text="", font=("Helvetica", 12, "bold"))
        status_lbl.pack(pady=5)

        def confirm():
            raw = entry.get().strip()

            if not raw.replace('.', '', 1).isdigit():  # Sayı kontrolü
                status_lbl.configure(text="⚠️ Lütfen geçerli bir sayı girin!", text_color="#e74c3c")
                return

            val = float(raw)
            zam_tipi = type_var.get()

            # Kullanıcının mevcut maaşını ve ID'sini bul
            self.app.db_manager.cursor.execute("SELECT id, salary FROM users WHERE username=?", (sender,))
            row = self.app.db_manager.cursor.fetchone()
            if not row: return
            u_id, current_salary = row

            # Zam yüzdesini hesapla (SalaryService yüzde formatında kayıt tuttuğu için)
            if zam_tipi == "Yüzde (%)":
                percent = val
            else:
                # Eğer 5000 TL girildiyse, bu mevcut maaşın yüzde kaçına denk geliyor onu hesaplıyoruz
                percent = (val / current_salary) * 100

            # SalaryService'i çağır
            record = self.app.salary_service.apply_raise(u_id, percent)

            if record:
                # İşlemleri onayla ve ekranları tazele
                self.app.hr_service.update_request_status(req_id, 'Onaylandı', 'Patron')
                self.app.notification_service.send(sender,
                                                   f"Talebiniz Patron tarafından onaylandı! Yeni Maaşınız: {record.new_salary:,.0f} ₺ ✅")

                status_lbl.configure(text=f"✅ {record.old_salary:,.0f} ₺ → {record.new_salary:,.0f} ₺",
                                     text_color="#2ecc71")

                self.load_staff_management()
                self.load_manager_approvals()
                self.update_stat_cards()

                win.after(1800, win.destroy)

        ctk.CTkButton(win, text="Onayla ve Uygula", command=confirm, fg_color="#2ecc71", width=160).pack(pady=10)
    def update_day(self, p_id, new_day):
        self.app.db_manager.cursor.execute("SELECT role FROM users WHERE id=?", (p_id,))
        result = self.app.db_manager.cursor.fetchone()

        if not result:
            return

        role = result[0]

        # Müdür ve Patron için kontrol yapma, direkt güncelle
        if role in ('Patron', 'Müdür'):
            self.app.hr_service.set_off_day_by_id(p_id, new_day)
            self.load_staff_management()
            return

        # Diğer roller için çakışma kontrolü
        ok, msg = self.app.hr_service.check_off_day_conflict(p_id, role, new_day)

        if not ok:
            win = ctk.CTkToplevel(self.app)
            win.title("Uyarı")
            win.geometry("320x160")
            win.grab_set()
            ctk.CTkLabel(win, text=f"⚠️ {msg}",
                         font=("Helvetica", 13, "bold"),
                         text_color="#e74c3c", wraplength=280).pack(pady=30)
            ctk.CTkButton(win, text="Tamam", command=win.destroy,
                          width=150, fg_color="#e74c3c").pack()
            return

        self.app.hr_service.set_off_day_by_id(p_id, new_day)
        self.load_staff_management()

    def fire_staff(self, p_id):
        self.app.hr_service.fire_employee(p_id)
        # Biri kovulduğunda her iki sekmeyi de güncellemek gerekir:
        self.load_staff_management()
        self.load_shift_reports()
        self.update_stat_cards()

    def change_salary(self, p_id, current_salary, amount):
        new_salary = current_salary + amount

        self.app.db_manager.cursor.execute(
            "UPDATE users SET salary=? WHERE id=?", (new_salary, p_id)
        )

        percent = (amount / current_salary) * 100
        import datetime
        date = datetime.date.today().isoformat()

        self.app.db_manager.cursor.execute(
            "INSERT INTO salary_records (user_id, old_salary, new_salary, percent, date) VALUES (?, ?, ?, ?, ?)",
            (p_id, current_salary, new_salary, percent, date)
        )

        self.app.db_manager.conn.commit()
        self.load_staff_management() # DEĞİŞEN YER
        self.update_stat_cards()
    def final_approve_raise(self, req_id):
        self.app.hr_service.db.cursor.execute(
            "SELECT sender_name FROM requests WHERE id=?", (req_id,)
        )
        sender = self.app.hr_service.db.cursor.fetchone()[0]

        self.app.hr_service.db.cursor.execute(
            "SELECT id FROM users WHERE username=?", (sender,)
        )
        result = self.app.hr_service.db.cursor.fetchone()

        if result:
            user_id = result[0]
            # Artık SalaryService kullanıyor — otomatik kayıt tutuyor
            record = self.app.salary_service.apply_raise(user_id, self._pending_percent)
            if record:
                print(f"Zam kaydedildi: {record}")

        self.app.hr_service.update_request_status(req_id, "Kesin Onaylandı")
        self.load_manager_approvals()
        self.load_salary_management()

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


    def load_shift_reports(self):
        for widget in self.tab_reports.winfo_children(): widget.destroy()

        # --- ÜST KISIM: İŞTEN ÇIKARMA EKRANI ---
        ctk.CTkLabel(self.tab_reports, text="🚨 Aktif Personel & İşten Çıkarma", font=("Helvetica", 16, "bold")).pack(
            pady=(10, 5))

        staff_scroll = ctk.CTkScrollableFrame(self.tab_reports, fg_color="transparent", height=160)
        staff_scroll.pack(fill="x", padx=20, pady=5)

        self.app.db_manager.cursor.execute("SELECT id, username, role FROM users WHERE role != 'Patron'")
        staff = self.app.db_manager.cursor.fetchall()

        if not staff:
            ctk.CTkLabel(staff_scroll, text="Aktif personel bulunmuyor.", text_color="gray").pack(pady=10)
        else:
            for p_id, name, role in staff:
                row = ctk.CTkFrame(staff_scroll, fg_color="#34495e", corner_radius=8)
                row.pack(fill="x", pady=3, padx=5)

                ctk.CTkLabel(row, text=f"👤 {name.capitalize()} ({role})", font=("Helvetica", 13, "bold"), width=150,
                             anchor="w").pack(side="left", padx=15, pady=8)

                # İşten Çıkar Butonu Buraya Geldi
                ctk.CTkButton(row, text="❌ İşten Çıkar", width=120, fg_color="#c0392b", hover_color="#a02e22",
                              command=lambda id=p_id: self.fire_staff(id)).pack(side="right", padx=15)

        # --- ALT KISIM: MESAİ TAKİBİ ---
        ctk.CTkLabel(self.tab_reports, text="📅 Günlük Mesai Raporları", font=("Helvetica", 16, "bold")).pack(
            pady=(20, 5))

        report_scroll = ctk.CTkScrollableFrame(self.tab_reports, fg_color="transparent")
        report_scroll.pack(fill="both", expand=True, padx=20, pady=5)

        all_shifts = self.app.hr_service.get_all_shifts()

        if not all_shifts:
            ctk.CTkLabel(report_scroll, text="Henüz bir kayıt bulunamadı.", font=("Helvetica", 14),
                         text_color="gray").pack(pady=40)
            return

        for shift_obj in all_shifts:
            color = "#2ecc71" if shift_obj.status == "Çalışıyor" else "#e74c3c"

            row = ctk.CTkFrame(report_scroll, fg_color="#2c3e50", corner_radius=8)
            row.pack(fill="x", pady=3, padx=5)

            ctk.CTkLabel(row, text=f"📅 {shift_obj.date}", width=100, font=("Helvetica", 12, "bold")).pack(side="left",
                                                                                                          padx=15,
                                                                                                          pady=8)
            ctk.CTkLabel(row, text=f"👤 {shift_obj.username.capitalize()}", width=150, anchor="w").pack(side="left",
                                                                                                       padx=10)
            ctk.CTkLabel(row, text=shift_obj.status, text_color=color, font=("Helvetica", 12, "bold")).pack(
                side="right", padx=20)
    def on_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab == "📊 Personel Takip":
            self.load_shift_reports()

