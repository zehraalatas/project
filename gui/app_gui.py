import customtkinter as ctk
from gui.login_screen import LoginScreen
from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.hr_service import HRService
from services.validation_service import ValidationService
from services.notification_service import NotificationService
from services.report_service import ReportService
from services.salary_service import SalaryService
from gui.login_screen import LoginScreen
from services.note_service import NoteService

class AppGUI(ctk.CTk):
    def __init__(self, db_manager, auth_service, hr_service,
                 validation_service, notification_service, report_service, salary_service, note_service):
        super().__init__()
        self.title("Kafe Yönetim Sistemi v1.0")
        self.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db_manager = db_manager
        self.auth_service = auth_service
        self.hr_service = hr_service
        self.validation_service = validation_service
        self.notification_service = notification_service
        self.report_service = report_service
        self.salary_service = salary_service
        self.current_user = None
        self.note_service = note_service

        self.show_login_screen()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_screen()
        LoginScreen(self)