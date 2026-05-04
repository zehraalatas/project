import datetime


class LeaveRequest:
    def __init__(self, request_id, sender, detail, status="Pending", date=None):
        """
        Represents a formal leave request from a staff member.

        :param status: Can be 'Pending', 'Pending Manager', 'Pending Boss', 'Approved', or 'Rejected'
        :param detail: The specific day or reason for the leave
        """
        self.request_id = request_id
        self.sender = sender
        self.detail = detail
        self.status = status
        self.date = date or datetime.date.today().isoformat()
        self.request_type = "Leave"  # Updated from 'İzin' to 'Leave'

    def is_pending(self):
        """Checks if the request is still in any pending state"""
        return "Pending" in self.status

    def __repr__(self):
        """Professional string representation for logging and debugging"""
        return f"LeaveRequest(ID: {self.request_id}, Sender: {self.sender}, Status: {self.status})"