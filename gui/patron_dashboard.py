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

        # 3. Sekmeleri (Tabview) oluştur
        self.tabview = ctk.CTkTabview(app)
        self.tabview.pack(pady=5, padx=20, fill="both", expand=True)

        self.tab_staff = self.tabview.add("🛠️ Takvim & İşten Çıkarma")
        self.tab_salary = self.tabview.add("💰 Maaş Yönetimi")
        self.tab_approvals = self.tabview.add("📩 Müdür Onayları")

        self.load_staff_management()
        self.load_salary_management()
        self.load_manager_approvals()

        self.logout_btn = ctk.CTkButton(app, text="Güvenli Çıkış", command=self.app.show_login_screen,
                                        fg_color="darkred")
        self.logout_btn.pack(side="bottom", pady=10)
        self.tabview.add("📊 Personel Takip")
        self.tab_reports = self.tabview.tab("📊 Personel Takip")
        # Sekme görünümünde (Tabview) değişiklik olduğunda çalışması için:
        self.tabview.configure(command=self.on_tab_change)



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
        # Önce ekranı temizle
        for widget in self.tab_staff.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_staff, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Patron hariç personelleri çek
        self.app.db_manager.cursor.execute("SELECT id, username, off_day, role FROM users WHERE role != 'Patron'")
        staff = self.app.db_manager.cursor.fetchall()

        # Gün listesi (Schedule.DAYS olarak da kullanılabilir)
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        for i, person in enumerate(staff, start=1):
            p_id, name, current_off, role = person

            # 1. Personel İsmi
            ctk.CTkLabel(scroll, text=f"{name.capitalize()}", font=("Helvetica", 14, "bold"), width=120).grid(
                row=i, column=0, padx=20, pady=10)

            # 2. Rol bazlı izin günü kontrolü
            if role == 'Müdür':
                role_count = 99  # Müdür her zaman izin alabilir
            else:
                self.app.db_manager.cursor.execute("SELECT COUNT(*) FROM users WHERE role=?", (role,))
                role_count = self.app.db_manager.cursor.fetchone()[0]

            # 3. İzin Günü Atama (Combo veya Kilit)
            if role_count <= 1:
                ctk.CTkLabel(scroll, text="🔒 Tek çalışan (İzin Yok)",
                             font=("Helvetica", 12), text_color="#e74c3c", width=180).grid(row=i, column=1, padx=10)

                ctk.CTkButton(scroll, text="Güncelle", width=80, fg_color="gray", state="disabled").grid(row=i,
                                                                                                         column=2,
                                                                                                         padx=5)
            else:
                combo = ctk.CTkComboBox(scroll, values=days, width=120)
                combo.set(current_off)
                combo.grid(row=i, column=1, padx=10)

                ctk.CTkButton(scroll, text="Güncelle", width=80, fg_color="#3498db",
                              command=lambda id=p_id, c=combo: self.update_day(id, c.get())).grid(row=i, column=2,
                                                                                                  padx=5)

            # 4. Yetki Kontrolü: Kovma Butonu (İşte eklediğimiz yer!)
            if self.user.can_fire():
                ctk.CTkButton(scroll, text="Kov (İşten Çıkar)", width=120, fg_color="#c0392b",
                              hover_color="#a02e22",
                              command=lambda id=p_id: self.fire_staff(id)).grid(row=i, column=3, padx=20)
            else:
                # Patron değilse butonu hiç gösterme ya da pasif yap (Örn: Müdür bakıyorsa)
                ctk.CTkLabel(scroll, text="Yetki Yok", text_color="gray").grid(row=i, column=3, padx=20)

    def load_salary_management(self):
        for widget in self.tab_salary.winfo_children(): widget.destroy()
        scroll = ctk.CTkScrollableFrame(self.tab_salary, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.app.db_manager.cursor.execute("SELECT id, username, salary FROM users WHERE role != 'Patron'")
        staff = self.app.db_manager.cursor.fetchall()

        for i, person in enumerate(staff, start=1):
            p_id, name, salary = person
            ctk.CTkLabel(scroll, text=f"{name.capitalize()} - {salary} ₺", font=("Helvetica", 14, "bold")).grid(row=i,
                                                                                                                column=0,
                                                                                                                padx=20,
                                                                                                                pady=10)
            ctk.CTkButton(scroll, text="+ Zam Yap", width=80, fg_color="#27ae60",
                          command=lambda id=p_id, s=salary: self.change_salary(id, s, 1000)).grid(row=i, column=1,
                                                                                                  padx=5)
            ctk.CTkButton(scroll, text="- Maaş Düşür", width=80, fg_color="#e67e22",
                          command=lambda id=p_id, s=salary: self.change_salary(id, s, -1000)).grid(row=i, column=2,
                                                                                                   padx=5)

    def load_manager_approvals(self):
        for widget in self.tab_approvals.winfo_children(): widget.destroy()
        raises = self.app.hr_service.get_forwarded_raises()

        if not raises:
            ctk.CTkLabel(self.tab_approvals, text="Bekleyen zam talebi yok.",
                         font=("Helvetica", 14), text_color="gray").pack(pady=40)
            return

        for req in raises:
            r_id, sender, r_type, detail, status = req
            frame = ctk.CTkFrame(self.tab_approvals)
            frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(frame, text=f"👤 {sender.capitalize()} - ZAM TALEBİ ({detail})",
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)
            ctk.CTkButton(frame, text="Son Onayı Ver", width=120, fg_color="#2ecc71",
                          command=lambda r=r_id, s=sender: self.open_raise_popup(r, s)).pack(side="right", padx=10)

    def open_raise_popup(self, req_id, sender):
        win = ctk.CTkToplevel(self.app)
        win.title("Zam Oranı Belirle")
        win.geometry("320x230")
        win.grab_set()

        ctk.CTkLabel(win, text=f"💰 {sender.capitalize()} için zam oranı",
                     font=("Helvetica", 15, "bold")).pack(pady=20)

        entry_frame = ctk.CTkFrame(win, fg_color="transparent")
        entry_frame.pack()

        percent_entry = ctk.CTkEntry(entry_frame, placeholder_text="Örn: 10", width=180, height=40)
        percent_entry.pack(side="left", padx=5)
        ctk.CTkLabel(entry_frame, text="%", font=("Helvetica", 18, "bold")).pack(side="left")

        status_lbl = ctk.CTkLabel(win, text="", font=("Helvetica", 12, "bold"))
        status_lbl.pack(pady=8)

        def confirm():
            raw = percent_entry.get().strip()

            if not self.app.validation_service.is_numeric(raw) or \
                    not self.app.validation_service.is_valid_percent(raw):
                status_lbl.configure(text="⚠️ Geçerli bir oran girin (1-100)!", text_color="#e74c3c")
                return

            percent = float(raw)

            # --- KRİTİK DÜZELTME BURASI ---
            # 1. Kullanıcı ID'sini bul
            self.app.db_manager.cursor.execute("SELECT id FROM users WHERE username=?", (sender,))
            u_id = self.app.db_manager.cursor.fetchone()[0]

            # 2. SalaryService'i çağır (Bu hem users'ı günceller hem record atar)
            record = self.app.salary_service.apply_raise(u_id, percent)

            if record:
                # 3. İlgili talebi veritabanında 'Kesin Onaylandı' olarak kapat
                self.app.hr_service.update_request_status(req_id, 'Kesin Onaylandı')

                status_lbl.configure(
                    text=f"✅ {record.old_salary:,.0f} ₺ → {record.new_salary:,.0f} ₺",
                    text_color="#2ecc71"
                )

                # Ekranları tazele
                self.load_salary_management()
                self.load_manager_approvals()
                self.update_stat_cards()

                win.after(1800, win.destroy)

        ctk.CTkButton(win, text="Onayla ve Uygula", command=confirm,
                      fg_color="#2ecc71", width=200, height=40).pack(pady=10)

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
        self.load_staff_management()
        self.load_salary_management()
        self.update_stat_cards()  # YENİ: Biri kovulunca üstteki "Aktif Çalışan" sayısını anında düşürür

    def change_salary(self, p_id, current_salary, amount):
        new_salary = current_salary + amount

        # 1. Veritabanında ana tabloyu güncelle
        self.app.db_manager.cursor.execute(
            "UPDATE users SET salary=? WHERE id=?", (new_salary, p_id)
        )

        # 2. YENİ: SalaryService kullanarak geçmiş kaydı (Record) oluştur
        # Sabit miktar olduğu için yüzdeyi (amount/current_salary)*100 olarak hesaplayabiliriz
        percent = (amount / current_salary) * 100
        import datetime
        date = datetime.date.today().isoformat()

        self.app.db_manager.cursor.execute(
            "INSERT INTO salary_records (user_id, old_salary, new_salary, percent, date) VALUES (?, ?, ?, ?, ?)",
            (p_id, current_salary, new_salary, percent, date)
        )

        self.app.db_manager.conn.commit()
        self.load_salary_management()
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


    def load_shift_reports(self):
        # Eski verileri temizle
        for widget in self.tab_reports.winfo_children():
            widget.destroy()

        # Servis üzerinden Shift nesnelerini çek
        all_shifts = self.app.hr_service.get_all_shifts()

        if not all_shifts:
            ctk.CTkLabel(self.tab_reports, text="Henüz bir kayıt bulunamadı.", font=("Helvetica", 14)).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.tab_reports, width=750, height=400, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=10)

        for shift_obj in all_shifts:
            # Shift nesnesinin status özelliğine göre renk seç
            color = "#2ecc71" if shift_obj.status == "Çalışıyor" else "#e74c3c"

            row = ctk.CTkFrame(scroll, fg_color="#34495e", corner_radius=8)
            row.pack(fill="x", pady=5, padx=10)

            # Nesne üzerinden verilere erişim
            ctk.CTkLabel(row, text=f"📅 {shift_obj.date}", width=120, font=("Helvetica", 12, "bold")).pack(side="left",
                                                                                                          padx=10)
            ctk.CTkLabel(row, text=f"👤 {shift_obj.username.capitalize()}", width=150).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=shift_obj.status, text_color=color, font=("Helvetica", 12, "bold")).pack(side="left",
                                                                                                            padx=20)

    def on_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab == "📊 Personel Takip":
            self.load_shift_reports()