import datetime

class Note:
    def __init__(self, note_id, sender_name, sender_role, target_role, content, date=None):
        self.note_id = note_id
        self.sender_name = sender_name
        self.sender_role = sender_role
        self.target_role = target_role  # Hangi rolün göreceği (Örn: Barista)
        self.content = content
        self.date = date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def __repr__(self):
        return f"Note({self.sender_name} -> {self.target_role}: {self.content})"