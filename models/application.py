class JobApplication:
    def __init__(self, app_id, name, desired_role, status):
        """
        Represents a candidate's application for a position.

        :param app_id: Unique database ID
        :param name: Candidate's full name
        :param desired_role: The role they applied for (e.g., Waiter, Chef)
        :param status: Current state (Pending, Approved, Rejected)
        """
        self.app_id = app_id
        self.name = name
        self.desired_role = desired_role
        self.status = status