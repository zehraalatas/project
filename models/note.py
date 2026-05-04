import datetime


class Note:
    def __init__(self, note_id, sender_name, sender_role, target_role, content, date=None):
        """
        Represents a communication entry on the digital notice board.

        :param sender_name: Username of the person posting the note
        :param sender_role: Role of the sender (e.g., Manager, Boss)
        :param target_role: The specific role group intended to see the note
        :param content: The message body
        :param date: Timestamp of the post
        """
        self.note_id = note_id
        self.sender_name = sender_name
        self.sender_role = sender_role
        self.target_role = target_role  # e.g., 'Barista', 'Waiter', 'All'
        self.content = content
        # Standardized date-time format for consistency across the board
        self.date = date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def __repr__(self):
        """Professional string representation for the communication log"""
        return f"Note(From: {self.sender_name} To: {self.target_role} | Content: {self.content[:20]}...)"