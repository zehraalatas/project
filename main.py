from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.hr_service import HRService
from services.validation_service import ValidationService
from services.notification_service import NotificationService
from services.report_service import ReportService
from services.salary_service import SalaryService
from gui.app_gui import AppGUI
from services.note_service import NoteService


def main():
    db = DatabaseManager()

    auth = AuthService(db)
    hr = HRService(db)
    validation = ValidationService()
    notification = NotificationService(db)
    report = ReportService(db)
    salary = SalaryService(db)
    note = NoteService(db)

    app = AppGUI(db_manager=db, auth_service=auth, hr_service=hr,
                 validation_service=validation, notification_service=notification,
                 report_service=report, salary_service=salary,note_service=note)
    app.mainloop()
    db.close_connection()

if __name__ == "__main__":
    main()