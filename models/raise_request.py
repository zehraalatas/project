import datetime


class RaiseRequest:
    def __init__(self, request_id, sender, detail, status="Pending", date=None):
        """
        Represents a salary raise request.

        :param status: Pending, Pending Manager, Pending Boss, Approved, Rejected
        :param detail: The requested amount or percentage (e.g., '10%')
        """
        self.request_id = request_id
        self.sender = sender
        self.detail = detail
        self.status = status
        self.date = date or datetime.date.today().isoformat()
        self.request_type = "Salary"  # Updated from 'Zam' to 'Salary'

    def is_pending(self):
        """Checks if the request is still awaiting any level of approval"""
        return "Pending" in self.status

    def is_forwarded_to_boss(self):
        """Checks if the manager has already approved and sent it to the boss"""
        return self.status == "Pending Boss"

    def __repr__(self):
        """Professional string representation"""
        return f"RaiseRequest(Sender: {self.sender}, Status: {self.status})"