import sqlite3

class DatabaseManager:
    def __init__(self, db_name="cafe_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Kullanıcılar Tablosu (off_day sütunu eklendi)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                username
                                TEXT
                                UNIQUE,
                                password
                                TEXT,
                                role
                                TEXT,
                                salary
                                REAL,
                                manager_id
                                INTEGER,
                                off_day
                                TEXT
                            )
                            """)

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS applications
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT,
                                desired_role
                                TEXT,
                                status
                                TEXT
                            )
                            """)

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS requests
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                sender_name
                                TEXT,
                                request_type
                                TEXT,
                                detail
                                TEXT,
                                status
                                TEXT
                            )
                            """)

        # YENİ: Mesai Kayıtları Tablosu (Kimin hangi gün çalıştığını tutar)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS shifts
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                user_id
                                INTEGER,
                                username
                                TEXT,
                                date
                                TEXT,
                                status
                                TEXT
                            )
                            """)


        # Varsayılan Hesaplar (İzin günleri Pazartesi olarak ayarlandı)
        self.cursor.execute("SELECT * FROM users WHERE role='Patron'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)", ('admin', 'admin123', 'Patron', 0.0, None, 'Pazartesi'))

        self.cursor.execute("SELECT * FROM users WHERE role='Müdür'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)", ('mudur', 'mudur123', 'Müdür', 35000.0, None, 'Pazartesi'))

        self.cursor.execute("SELECT * FROM users WHERE role='Garson'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role, salary, manager_id, off_day) VALUES (?, ?, ?, ?, ?, ?)", ('garson', 'garson123', 'Garson', 20000.0, 2, 'Pazartesi'))

        self.conn.commit()