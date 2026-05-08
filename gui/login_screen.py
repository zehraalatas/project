import customtkinter as ctk
from gui.apply_screen import ApplyScreen
from gui.admin_dashboard import AdminDashboard
from gui.manager_dashboard import ManagerDashboard
from gui.employee_dashboard import EmployeeDashboard


class LoginScreen:
    def __init__(self, app):
        self.app = app

        # Center Frame for Login
        self.main_frame = ctk.CTkFrame(app, width=400, height=500, corner_radius=12)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Screen Title
        self.label_title = ctk.CTkLabel(self.main_frame, text="☕ System Login ☕", font=("Arial", 24, "bold"))
        self.label_title.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        # Input Fields
        self.user_input = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=250, height=40)
        self.user_input.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)

        self.pass_input = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=250, height=40)
        self.pass_input.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.pass_input.bind('<Return>', self.login)

        # Login and Apply Buttons
        self.btn_login = ctk.CTkButton(self.main_frame, text="Login", command=self.login, width=250, height=40)
        self.btn_login.place(relx=0.5, rely=0.65, anchor=ctk.CENTER)

        self.btn_apply = ctk.CTkButton(self.main_frame, text="Apply for Job", command=self.open_apply_screen,
                                       fg_color="transparent", border_width=1, width=250, height=40)
        self.btn_apply.place(relx=0.5, rely=0.78, anchor=ctk.CENTER)

        # Error Message Area
        self.info_label = ctk.CTkLabel(self.main_frame, text="", text_color="red")
        self.info_label.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

    def login(self, event=None):
        # Taking inputs from entries
        uname = self.user_input.get().strip()
        pword = self.pass_input.get().strip()


        # Check user from authentication service
        found_user = self.app.auth_service.login(uname, pword)

        if found_user:
            self.app.current_user = found_user
            self.app.clear_screen()

            # Simple if-else logic for dashboards (Student level coding)
            if found_user.role == "Boss":
                AdminDashboard(self.app)
            elif found_user.role == "Manager":
                ManagerDashboard(self.app)
            else:
                # Default for all other employees
                EmployeeDashboard(self.app)
        else:
            # Showing error in English
            self.info_label.configure(text="Invalid username or password!")

    def open_apply_screen(self):
        """Changes screen to job application form"""
        self.app.clear_screen()
        ApplyScreen(self.app)