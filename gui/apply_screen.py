import customtkinter as ctk


class ApplyScreen:
    def __init__(self, app):
        self.app = app

        # Frame setup
        self.frame = ctk.CTkFrame(app, width=400, height=450, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Title
        self.title = ctk.CTkLabel(self.frame, text="Job Application", font=("Arial", 24, "bold"))
        self.title.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        # Name Entry
        self.name_entry = ctk.CTkEntry(self.frame, placeholder_text="Full Name", width=250, height=40)
        self.name_entry.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)

        # Roles - Using a SET for unique values (Lesson Topic: Set)
        roles_set = {"Waiter", "Chef", "Cashier", "Cleaner", "Barista"}
        self.role_combo = ctk.CTkComboBox(self.frame, values=sorted(list(roles_set)), width=250, height=40)
        self.role_combo.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Buttons
        self.apply_btn = ctk.CTkButton(self.frame, text="Submit Application", command=self.submit, width=250, height=40)
        self.apply_btn.place(relx=0.5, rely=0.65, anchor=ctk.CENTER)

        # BURASI DÜZELDİ: start_login yerine show_login_screen yaptık
        self.back_btn = ctk.CTkButton(self.frame, text="Go Back", command=self.app.show_login_screen,
                                      fg_color="gray", width=250)
        self.back_btn.place(relx=0.5, rely=0.78, anchor=ctk.CENTER)

        # Status
        self.status_label = ctk.CTkLabel(self.frame, text="")
        self.status_label.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

    def submit(self):
        # Using a DICTIONARY to handle data (Lesson Topic: Dictionary)
        name = self.name_entry.get()
        role = self.role_combo.get()

        if name != "":
            app_info = {
                "name": name,
                "job": role
            }

            # BURASI DÜZELDİ: hr yerine hr_service yaptık
            self.app.hr_service.submit_application(app_info["name"], app_info["job"])

            self.status_label.configure(text="Success! Application sent.", text_color="green")
            self.name_entry.delete(0, 'end')
        else:
            self.status_label.configure(text="Please enter your name!", text_color="red")