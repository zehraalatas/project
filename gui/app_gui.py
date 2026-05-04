import customtkinter as ctk
from gui.login_screen import LoginScreen


class AppGUI(ctk.CTk):
    def __init__(self, db_manager, auth_service, hr_service,
                 validation_service, notification_service, report_service, salary_service, note_service):
        super().__init__()

        # Orijinal başlık ve boyutlar
        self.title("Cafe Management System")
        self.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # İsimleri bozmadım ama iç yapıdaki atamaları sadeleştirdim
        self.db_manager = db_manager
        self.auth_service = auth_service
        self.hr_service = hr_service
        self.validation_service = validation_service
        self.notification_service = notification_service
        self.report_service = report_service
        self.salary_service = salary_service
        self.note_service = note_service

        self.current_user = None

        self.show_login_screen()

    def clear_screen(self):
        """Clears all widgets from the window"""
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Goes back to the login page"""
        self.clear_screen()
        LoginScreen(self)

        def setup_off_day_area(self, parent_frame, employee):
            count = self.hr_service.get_role_count(employee.role)

            for widget in parent_frame.winfo_children():
                widget.destroy()

            if count <= 1:
                # Tek kişi varsa Kırmızı Uyarı Label'ı
                info_label = ctk.Label(
                    parent_frame,
                    text=f"ONLY {employee.role.upper()} (No Off-Day Allowed)",
                    fg="white",
                    bg="#cc0000",
                    font=("Arial", 10, "bold"),
                    padx=10,
                    pady=5
                )
                info_label.pack(fill="x")
            else:
                # Birden fazla kişi varsa Seçim Combobox'ı
                ctk.Label(parent_frame, text="Select Off-Day:", font=("Arial", 10)).pack(side="left")

                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                self.off_day_combo = ctk.Combobox(parent_frame, values=days, state="readonly")
                self.off_day_combo.set(employee.off_day)
                self.off_day_combo.pack(side="left", padx=10)