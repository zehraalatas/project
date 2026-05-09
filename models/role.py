class Role:
    # Sabit değerler
    BOSS = "Boss"
    MANAGER = "Manager"
    WAITER = "Waiter"
    BARISTA = "Barista"
    CHEF = "Chef"
    CLEANER = "Cleaner"
    CASHIER = "Cashier"

    def get_employee_roles(self):
        return [
            self.WAITER,
            self.BARISTA,
            self.CHEF,
            self.CLEANER,
            self.CASHIER
        ]
