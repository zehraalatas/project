import customtkinter as ctk
from gui.apply_screen import ApplyScreen
from gui.patron_dashboard import PatronDashboard
from gui.manager_dashboard import ManagerDashboard
from gui.employee_dashboard import EmployeeDashboard


class LoginScreen:
    def __init__(self, app):
        self.app = app

        # Merkez Frame
        self.frame = ctk.CTkFrame(app, width=400, height=500, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.title = ctk.CTkLabel(self.frame, text="Sisteme Giriş", font=("Helvetica", 24, "bold"))
        self.title.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Kullanıcı Adı", width=250, height=40)
        self.username_entry.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Şifre", show="*", width=250, height=40)
        self.password_entry.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.login_btn = ctk.CTkButton(self.frame, text="Giriş Yap", command=self.login, width=250, height=40,
                                       font=("Helvetica", 14, "bold"))
        self.login_btn.place(relx=0.5, rely=0.65, anchor=ctk.CENTER)

        self.apply_btn = ctk.CTkButton(self.frame, text="İşe Başvur", command=self.open_apply_screen,
                                       fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"),
                                       width=250, height=40)
        self.apply_btn.place(relx=0.5, rely=0.78, anchor=ctk.CENTER)

        self.error_label = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.error_label.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.app.auth_service.login(username, password)

        if user:
            self.app.current_user = user
            if user.role == "Patron":
                self.app.clear_screen()
                PatronDashboard(self.app)
            elif user.role == "Müdür":
                self.app.clear_screen()
                ManagerDashboard(self.app)
            else:
                self.app.clear_screen()
                EmployeeDashboard(self.app)
        else:
            self.error_label.configure(text="Hatalı kullanıcı adı veya şifre!")

    def open_apply_screen(self):
        self.app.clear_screen()
        ApplyScreen(self.app)