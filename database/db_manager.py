import sqlite3


class DatabaseManager:
    def __init__(self, db_name="cafe_system.db"):
        # Create connection to the SQLite database
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):

        # 1. Users Table: Stores all staff info
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

        # 2. Applications Table: For job seekers
        # db_manager.py içindeki tablo oluşturma kısmına ekle:
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
                                surname
                                TEXT,
                                gender
                                TEXT,
                                email
                                TEXT,
                                phone
                                TEXT,
                                experience
                                TEXT,
                                notes
                                TEXT,
                                desired_role
                                TEXT,
                                status
                                TEXT
                            )
                            """)

        # 3. Requests Table: For staff leave and salary raise requests
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

        # 4. Shifts Table: Tracks daily working status
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
                                TEXT,
                                hours
                                INTEGER
                                DEFAULT
                                8
                            )
                            """)

        # --- SEEDING DEFAULT USERS ---
        # Using a List of Tuples for easy management (Lesson Topic: Collections)
        default_accounts = [
            ('admin', 'admin123', 'Boss', 500000.0, None, 'Monday'),
            ('manager', 'manager123', 'Manager', 35000.0, None, 'Monday')

        ]

        for user_data in default_accounts:
            # We check by username to prevent 'UNIQUE constraint failed' errors
            self.cursor.execute("SELECT * FROM users WHERE username=?", (user_data[0],))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                                    INSERT INTO users (username, password, role, salary, manager_id, off_day)
                                    VALUES (?, ?, ?, ?, ?, ?)""", user_data)

        # Finalize and save all changes
        self.conn.commit()
        print("✅ Database initialized successfully with English schema.")

    def close_connection(self):
        """Safely closes the database connection"""
        self.conn.close()