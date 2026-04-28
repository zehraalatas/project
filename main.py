from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.hr_service import HRService
from gui.app_gui import AppGUI


def main():
    # 1. Veritabanını Başlat
    db = DatabaseManager()

    # 2. Servisleri Başlat
    auth = AuthService(db)
    hr = HRService(db)

    # 3. GUI'yi Başlat ve Sistemi İçine Enjekte Et (Dependency Injection)
    app = AppGUI(db_manager=db, auth_service=auth, hr_service=hr)
    app.mainloop()


if __name__ == "__main__":
    main()