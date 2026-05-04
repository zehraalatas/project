class Role:
    # Constants for database and logic checks
    BOSS = "Boss"           # Eski: Patron
    MANAGER = "Manager"     # Eski: Müdür
    WAITER = "Waiter"       # Eski: Garson
    BARISTA = "Barista"
    CHEF = "Chef"           # Eski: Aşçı
    CLEANER = "Cleaner"     # Eski: Temizlikçi
    CASHIER = "Cashier"     # Eski: Kasiyer

    @staticmethod
    def get_employee_roles():
        """
        Lists only standard staff positions for the job application screen.
        Boss or Manager positions cannot be applied for directly.
        """
        return [
            Role.WAITER,
            Role.BARISTA,
            Role.CHEF,
            Role.CLEANER,
            Role.CASHIER
        ]

    @staticmethod
    def get_all_roles():
        """Returns every role defined in the system for administrative use."""
        return [
            Role.BOSS, Role.MANAGER, Role.WAITER,
            Role.BARISTA, Role.CHEF, Role.CLEANER, Role.CASHIER
        ]