class JobApplication:
    def __init__(self, app_id, name, desired_role, status):
        self.app_id = app_id
        self.name = name
        self.desired_role = desired_role
        self.status = status # "Pending", "Approved", "Rejected"