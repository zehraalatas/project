class Role:
    # Sabit değerler (Veritabanı ile eşleşenler)
    BOSS = "Boss"
    MANAGER = "Manager"
    WAITER = "Waiter"
    BARISTA = "Barista"
    CHEF = "Chef"
    CLEANER = "Cleaner"
    CASHIER = "Cashier"

    def __init__(self):
        # Bu sınıfı nesne olarak oluşturduğumuzda
        # varsayılan bir rol listesi tutabiliriz.
        pass

    def get_employee_roles(self):
        """
        Sadece iş başvurusu yapılabilen pozisyonları döndürür.
        Admin ve Müdür pozisyonlarını listeden çıkarır.
        """
        return [
            self.WAITER,
            self.BARISTA,
            self.CHEF,
            self.CLEANER,
            self.CASHIER
        ]

    def get_all_roles(self):
        """Sistemdeki istisnasız tüm rolleri döndürür."""
        return [
            self.BOSS, self.MANAGER, self.WAITER,
            self.BARISTA, self.CHEF, self.CLEANER, self.CASHIER
        ]