from models.user import User


class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager

    def login(self, username, password):
        self.db.cursor.execute(
            "SELECT id, username, role, salary, manager_id, off_day FROM users WHERE username=? AND password=?",
            (username, password))
        result = self.db.cursor.fetchone()
        if result:
            return User(result[0], result[1], result[2], result[3], result[4], result[5])
        return None

    # YENİ EKLENEN KISIM: Ayarları Güncelleme
    def update_credentials(self, user_id, new_username, new_password):
        # Yeni ismin başkası tarafından kullanılıp kullanılmadığını kontrol et
        self.db.cursor.execute("SELECT id FROM users WHERE username=? AND id!=?", (new_username, user_id))
        if self.db.cursor.fetchone():
            return False, "Bu kullanıcı adı zaten alınmış!"

        # Kullanıcıyı güncelle
        self.db.cursor.execute("UPDATE users SET username=?, password=? WHERE id=?",
                               (new_username, new_password, user_id))
        self.db.conn.commit()
        return True, "Bilgiler başarıyla güncellendi!"