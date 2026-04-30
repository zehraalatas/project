import customtkinter as ctk


class PatronDashboard:
    def __init__(self, app):
        self.app = app

        # Üst İstatistik Kartları Çerçevesi
        self.stat_frame = ctk.CTkFrame(app, fg_color="transparent")
        self.stat_frame.pack(pady=15)  # Ortada durması için padx/fill kaldırdık

        # Kartları çizen fonksiyonu çağırıyoruz
        self.update_stat_cards()

        # Sekmeler
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

    # YENİ: Kartları Dinamik Güncelleyen Fonksiyon
    def update_stat_cards(self):
        # Önce eski kartları temizle (Yenilenirken üst üste binmesin)
        for widget in self.stat_frame.winfo_children():
            widget.destroy()

        # Veritabanına bağlanıp Patron hariç herkesi sayıyoruz
        self.app.db_manager.cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'Patron'")
        aktif_personel = self.app.db_manager.cursor.fetchone()[0]

        # 3 Adet Kartı Ekrana Basıyoruz
        self.create_stat_card(self.stat_frame, "Günlük Kasa", "14.250 ₺", "#2ecc71", 0)
        self.create_stat_card(self.stat_frame, "Müşteri Sayısı", "142", "#3498db", 1)
        self.create_stat_card(self.stat_frame, "Aktif Çalışan", f"{aktif_personel}", "#f1c40f", 2)

    def create_stat_card(self, parent, title, value, color, col):
        # Kartın tasarımını biraz daha oval ve şık yaptık
        card = ctk.CTkFrame(parent, width=200, height=80, border_width=2, border_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=15)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Helvetica", 14, "bold"), text_color="gray").pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=("Helvetica", 22, "bold"), text_color=color).pack()

    def load_staff_management(self):
        for widget in self.tab_staff.winfo_children(): widget.destroy()
        scroll = ctk.CTkScrollableFrame(self.tab_staff, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.app.db_manager.cursor.execute("SELECT id, username, off_day, role FROM users WHERE role != 'Patron'")
        staff = self.app.db_manager.cursor.fetchall()

        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        for i, person in enumerate(staff, start=1):
            p_id, name, current_off, role = person

            # Rolden kaç kişi var kontrol et
            # Bununla değiştir:
            if role in ('Patron', 'Müdür'):
                role_count = 99  # Müdür ve patron için her zaman izin atanabilir
            else:
                self.app.db_manager.cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role=?", (role,)
                )
                role_count = self.app.db_manager.cursor.fetchone()[0]

            ctk.CTkLabel(scroll, text=f"{name.capitalize()}", font=("Helvetica", 14, "bold")).grid(
                row=i, column=0, padx=20, pady=10)

            if role_count <= 1:
                # Tek kişi — izin günü atanamaz, combo yerine kilitli etiket
                ctk.CTkLabel(scroll, text="🔒 İzin Yok (Tek çalışan)",
                             font=("Helvetica", 12), text_color="#e74c3c", width=180).grid(
                    row=i, column=1, padx=10)

                # Güncelle butonu da devre dışı
                ctk.CTkButton(scroll, text="Güncelle", width=80, fg_color="gray", state="disabled").grid(
                    row=i, column=2, padx=5)
            else:
                combo = ctk.CTkComboBox(scroll, values=days, width=120)
                combo.set(current_off)
                combo.grid(row=i, column=1, padx=10)

                ctk.CTkButton(scroll, text="Güncelle", width=80, fg_color="#3498db",
                              command=lambda id=p_id, c=combo: self.update_day(id, c.get())).grid(
                    row=i, column=2, padx=5)

            ctk.CTkButton(scroll, text="Kov (İşten Çıkar)", width=120, fg_color="#c0392b",
                          command=lambda id=p_id: self.fire_staff(id)).grid(row=i, column=3, padx=20)

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

        percent_entry = ctk.CTkEntry(entry_frame, placeholder_text="Örn: 10", width=180, height=40,
                                     font=("Helvetica", 14))
        percent_entry.pack(side="left", padx=5)
        ctk.CTkLabel(entry_frame, text="%", font=("Helvetica", 18, "bold")).pack(side="left")

        status_lbl = ctk.CTkLabel(win, text="", font=("Helvetica", 12, "bold"))
        status_lbl.pack(pady=8)

        def confirm():
            raw = percent_entry.get().strip()

            # Sadece sayı ve nokta kabul et
            if not raw.replace(".", "", 1).isdigit():
                status_lbl.configure(text="⚠️ Lütfen geçerli bir sayı girin!", text_color="#e74c3c")
                return

            percent = float(raw)

            if percent <= 0 or percent > 100:
                status_lbl.configure(text="⚠️ Oran 0 ile 100 arasında olmalı!", text_color="#e74c3c")
                return

            old_sal, new_sal = self.app.hr_service.final_approve_raise(req_id, percent)

            status_lbl.configure(
                text=f"✅ {old_sal:,.0f} ₺ → {new_sal:,.0f} ₺",
                text_color="#2ecc71"
            )
            self.load_salary_management()  # Maaş sekmesini anında güncelle
            self.load_manager_approvals()  # Listeyi temizle
            win.after(1800, win.destroy)

        ctk.CTkButton(win, text="Onayla ve Uygula", command=confirm,
                      fg_color="#2ecc71", width=200, height=40,
                      font=("Helvetica", 13, "bold")).pack(pady=10)

    def update_day(self, p_id, new_day):
        # Kişinin rolünü al
        self.app.db_manager.cursor.execute("SELECT role FROM users WHERE id=?", (p_id,))
        result = self.app.db_manager.cursor.fetchone()

        if not result:
            return

        role = result[0]

        # Çakışma kontrolü
        ok, msg = self.app.hr_service.check_off_day_conflict(p_id, role, new_day)

        if not ok:
            # Uyarı popup'ı
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
        self.app.db_manager.cursor.execute("UPDATE users SET salary=? WHERE id=?", (new_salary, p_id))
        self.app.db_manager.conn.commit()
        self.load_salary_management()

    def final_approve_raise(self, req_id):
        self.app.hr_service.update_request_status(req_id, "Kesin Onaylandı")
        self.load_manager_approvals()