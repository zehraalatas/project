import sqlite3

class DatabaseManager:
    def __init__(self, db_name="cafe_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
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

        default_accounts = [
            ('admin', 'admin123', 'Boss', 500000.0, None, 'Monday'),
            ('manager', 'manager123', 'Manager', 35000.0, None, 'Monday')

        ]

        for user_data in default_accounts:
            self.cursor.execute("SELECT * FROM users WHERE username=?", (user_data[0],))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                                    INSERT INTO users (username, password, role, salary, manager_id, off_day)
                                    VALUES (?, ?, ?, ?, ?, ?)""", user_data)

        self.conn.commit()

    def close_connection(self):
        self.conn.close()