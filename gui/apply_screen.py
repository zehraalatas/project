import customtkinter as ctk


class ApplyScreen:
    def __init__(self, app):
        self.app = app

        self.frame = ctk.CTkFrame(app, width=400, height=400, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.title = ctk.CTkLabel(self.frame, text="İş Başvurusu", font=("Helvetica", 24, "bold"))
        self.title.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        self.name_entry = ctk.CTkEntry(self.frame, placeholder_text="Adınız Soyadınız", width=250, height=40)
        self.name_entry.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)

        self.role_combo = ctk.CTkComboBox(self.frame, values=["Garson", "Aşçı", "Kasiyer","Temizlikçi","Barista"], width=250, height=40)
        self.role_combo.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.apply_btn = ctk.CTkButton(self.frame, text="Başvuruyu Gönder", command=self.submit, width=250, height=40)
        self.apply_btn.place(relx=0.5, rely=0.65, anchor=ctk.CENTER)

        self.back_btn = ctk.CTkButton(self.frame, text="Geri Dön", command=self.app.show_login_screen,
                                      fg_color="transparent", width=250)
        self.back_btn.place(relx=0.5, rely=0.78, anchor=ctk.CENTER)

        self.status_label = ctk.CTkLabel(self.frame, text="")
        self.status_label.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

    def submit(self):
        name = self.name_entry.get()
        role = self.role_combo.get()
        if name:
            self.app.hr_service.submit_application(name, role)
            self.status_label.configure(text="Başvuru alındı! Müdür onayı bekleniyor.", text_color="green")
            self.name_entry.delete(0, 'end')