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
            ctk.CTkLabel(scroll, text=f"{name.capitalize()}", font=("Helvetica", 14, "bold")).grid(row=i, column=0,
                                                                                                   padx=20, pady=10)

            combo = ctk.CTkComboBox(scroll, values=days, width=120)
            combo.set(current_off)
            combo.grid(row=i, column=1, padx=10)

            ctk.CTkButton(scroll, text="Güncelle", width=80, fg_color="#3498db",
                          command=lambda id=p_id, c=combo: self.update_day(id, c.get())).grid(row=i, column=2, padx=5)
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

        for req in raises:
            r_id, sender, r_type, detail, status = req
            frame = ctk.CTkFrame(self.tab_approvals)
            frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(frame, text=f"👤 {sender.capitalize()} - ZAM TALEBİ ({detail})",
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)
            ctk.CTkButton(frame, text="Son Onayı Ver", width=120, fg_color="#2ecc71",
                          command=lambda r=r_id: self.final_approve_raise(r)).pack(side="right", padx=10)

    def update_day(self, p_id, new_day):
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