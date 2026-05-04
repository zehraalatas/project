from models.work_day import WorkDay


class Schedule:
    def __init__(self, user_id, off_day_name):
        """
        Manages the weekly work schedule for a specific user.

        :param user_id: ID of the employee
        :param off_day_name: The day of the week marked as 'OFF' (e.g., 'Monday')
        """
        self.user_id = user_id
        # Standardized to English to match database and UI logic
        self.DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Filling the weekly plan with WorkDay objects
        self.weekly_plan = []
        for d in self.DAYS:
            # Check if the day matches the assigned off-day
            is_off = (d == off_day_name)
            # Create a WorkDay object for each day
            self.weekly_plan.append(WorkDay(d, is_off=is_off))

    def get_day_status(self, day_name):
        """
        Retrieves the work/off status for a specific day.

        :param day_name: Name of the day to search for
        :return: String summary of the day's status or error message
        """
        for wd in self.weekly_plan:
            if wd.day_name == day_name:
                return wd.get_summary()
        return "Day not found"

    def __repr__(self):
        """String representation for debugging"""
        return f"Schedule(UserID: {self.user_id}, Days: {len(self.weekly_plan)})"