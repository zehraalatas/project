import datetime

class LeaveRequest:
    def __init__(self, request_id, sender, detail, status="Bekliyor", date=None):
        self.request_id = request_id
        self.sender = sender
        self.detail = detail
        self.status = status
        self.date = date or datetime.date.today().isoformat()
        self.request_type = "İzin"

    def is_pending(self):
        return self.status == "Bekliyor"

    def __repr__(self):
        return f"LeaveRequest({self.sender}, {self.status})"