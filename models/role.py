class Role:
    # Veritabanı ve mantıksal kontroller için rollerin sabitleri (Constants)
    PATRON = "Patron"
    MUDUR = "Müdür"
    GARSON = "Garson"
    BARISTA = "Barista"
    ASCI = "Aşçı"
    TEMIZLIKCI = "Temizlikçi"
    KASIYER = "Kasiyer"

    @staticmethod
    def get_employee_roles():
        """
        Bu metod, iş başvuru ekranındaki açılır menüde (Combobox)
        sadece çalışan pozisyonlarını listelemek için kullanılacak.
        Patron veya Müdür pozisyonlarına doğrudan başvuru yapılamaz.
        """
        return [Role.GARSON, Role.BARISTA, Role.ASCI, Role.TEMIZLIKCI, Role.KASIYER]