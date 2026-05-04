import customtkinter as ctk
# Model imports
from models.application import JobApplication
from models.leave_request import LeaveRequest
from models.raise_request import RaiseRequest


class ManagerDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        # Header with capitalized username
        self.header = ctk.CTkLabel(app, text=f"👔 Manager Panel - Welcome {self.user.username.capitalize()}",
                                   font=("Arial", 26, "bold"))
        self.header.pack(pady=(20, 10))

        # Tabs for different sections
        self.tabs = ctk.CTkTabview(app, width=800, height=450)
        self.tabs.pack(pady=10, padx=20, fill="both", expand=True)

        self.profile_tab = self.tabs.add("👤 My Profile")
        self.request_tab = self.tabs.add("📨 Staff Requests")

        # Load initial data
        self.load_staff_requests()
        self.load_manager_profile()

        # Logout button
        self.btn_logout = ctk.CTkButton(app, text="Logout", command=self.app.show_login_screen,
                                        fg_color="darkred", width=150)
        self.btn_logout.pack(side="bottom", pady=20)

    def load_staff_requests(self):
        """Lists pending requests from staff for the Manager to review"""
        for widget in self.request_tab.winfo_children():
            widget.destroy()

        # Updated to 'Pending Manager' to match HRService logic
        query = "SELECT id, sender_name, request_type, detail, status FROM requests WHERE status='Pending Manager'"
        self.app.db_manager.cursor.execute(query)
        all_requests = self.app.db_manager.cursor.fetchall()

        if not all_requests:
            ctk.CTkLabel(self.request_tab, text="No pending requests found.",
                         font=("Arial", 14), text_color="gray").pack(pady=40)
            return

        scroll_view = ctk.CTkScrollableFrame(self.request_tab, fg_color="transparent")
        scroll_view.pack(fill="both", expand=True, pady=10)

        # Mapping request types for UI display
        type_labels = {"Leave": "Leave Request", "Salary": "Salary Raise"}

        for req in all_requests:
            r_id, sender, r_type, info, status = req
            row_frame = ctk.CTkFrame(scroll_view)
            row_frame.pack(pady=5, padx=20, fill="x")

            # Updated check for English types
            icon = "📅" if r_type == "Leave" else "💰"
            eng_type = type_labels.get(r_type, r_type)
            display_text = f"{icon} {sender.capitalize()} - {eng_type} ({info})"

            ctk.CTkLabel(row_frame, text=display_text, font=("Arial", 13, "bold")).pack(side="left", padx=20, pady=10)

            # Actions - Sending "Approved" or "Rejected" directly to HRService
            ctk.CTkButton(row_frame, text="Approve ✅", width=110, fg_color="#3498db",
                          command=lambda i=r_id, s=sender: self.update_request(i, "Approved", s)).pack(side="right", padx=10)

            ctk.CTkButton(row_frame, text="Reject ❌", width=90, fg_color="#e74c3c",
                          command=lambda i=r_id, s=sender: self.update_request(i, "Rejected", s)).pack(side="right", padx=10)

    def update_request(self, req_id, new_status, employee_name):
        """Handles the decision and sends notification based on new English schema"""
        # We now send "Approved"/"Rejected" directly. HRService handles 'Pending Boss' logic.
        success = self.app.hr_service.update_request_status(req_id, new_status, "Manager")

        if success:
            if new_status == "Approved":
                msg = "Approved by Manager, waiting for Boss approval. ⏳"
            else:
                msg = "Your request was rejected by the Manager. ❌"

            self.app.notification_service.send(employee_name, msg)

        self.load_staff_requests()

    def load_manager_profile(self):
        """Loads personal info and schedule for the logged-in Manager"""
        for widget in self.profile_tab.winfo_children():
            widget.destroy()

        self.app.db_manager.cursor.execute("SELECT role, salary, off_day FROM users WHERE username=?",
                                           (self.user.username,))
        data = self.app.db_manager.cursor.fetchone()
        u_role, u_salary, u_off = data if data else ("Manager", 0, "Monday")

        # Info labels
        ctk.CTkLabel(self.profile_tab, text=f"Role: {u_role} | Salary: {u_salary:,.0f} ₺",
                     font=("Arial", 15), text_color="gray").pack(pady=(10, 20))

        # Action Buttons
        ctk.CTkButton(self.profile_tab, text="🔔 Notifications", fg_color="#34495e", width=380, height=35).pack(pady=5)

        self.btn_board = ctk.CTkButton(self.profile_tab, text="📝 Department Communication",
                                       command=self.open_all_boards, fg_color="#8e44ad", width=380, height=35)
        self.btn_board.pack(pady=5)

        # Work Schedule
        ctk.CTkLabel(self.profile_tab, text="📅 Your Work Schedule", font=("Arial", 18, "bold")).pack(pady=(25, 15))

        days_box = ctk.CTkFrame(self.profile_tab, fg_color="transparent")
        days_box.pack(pady=5)

        short_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for idx, d_name in enumerate(day_names):
            column = ctk.CTkFrame(days_box, fg_color="transparent")
            column.grid(row=0, column=idx, padx=8)

            ctk.CTkLabel(column, text=short_days[idx], font=("Arial", 12, "bold")).pack(pady=5)

            is_holiday = (d_name == u_off)
            status_color = "#e74c3c" if is_holiday else "#2ecc71"
            status_text = "OFF" if is_holiday else "Work"

            day_card = ctk.CTkFrame(column, fg_color=status_color, width=85, height=75, corner_radius=8)
            day_card.pack_propagate(False)
            day_card.pack()

            ctk.CTkLabel(day_card, text=status_text, font=("Arial", 13, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # Request Buttons for Manager's own needs
        action_row = ctk.CTkFrame(self.profile_tab, fg_color="transparent")
        action_row.pack(pady=35)

        ctk.CTkButton(action_row, text="Request Leave", fg_color="#f39c12", width=150, height=40,
                      command=self.open_leave_dialog).pack(side="left", padx=15)

        ctk.CTkButton(action_row, text="Request Raise", fg_color="#8e44ad", width=150, height=40,
                      command=self.open_salary_dialog).pack(side="left", padx=15)

    def open_leave_dialog(self):
        """Popup for the Manager to request their own leave"""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Leave Request")
        dialog.geometry("300x200")
        dialog.grab_set()
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Select day for leave:", font=("Arial", 13, "bold")).pack(pady=(25, 5))

        eng_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selector = ctk.CTkComboBox(dialog, values=eng_days, width=180, state="readonly")
        selector.set("Select Day")
        selector.pack(pady=10)

        def confirm():
            val = selector.get()
            if val != "Select Day":
                # Manager's request goes to 'Pending Boss' status via service
                self.send_to_boss("Leave", val)
                dialog.destroy()

        ctk.CTkButton(dialog, text="Submit Request", fg_color="#f39c12", command=confirm).pack(pady=15)

    def open_salary_dialog(self):
        """Input dialog for the Manager to request their own raise"""
        dialog = ctk.CTkInputDialog(text="Enter raise details (e.g. 10%):", title="Salary Request")
        info = dialog.get_input()
        if info:
            self.send_to_boss("Salary", info)

    def send_to_boss(self, r_type, detail):
        """Forwards Manager's requests directly to the Boss"""
        self.app.hr_service.submit_manager_request(self.user.username, r_type, detail)
        self.app.notification_service.send(self.user.username, f"✅ Your {r_type} request sent to the Boss!")

    def open_all_boards(self):
        """Board to communicate with all department staff"""
        board_win = ctk.CTkToplevel(self.app)
        board_win.title("Global Communication Board")
        board_win.geometry("500x550")
        board_win.grab_set()

        ctk.CTkLabel(board_win, text="📝 Departmental Communication", font=("Arial", 18, "bold")).pack(pady=10)

        note_scroll = ctk.CTkScrollableFrame(board_win, fg_color="#2c3e50")
        note_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh():
            for child in note_scroll.winfo_children():
                child.destroy()

            all_notes = self.app.note_service.get_notes_for_user(self.user.role)
            if not all_notes:
                ctk.CTkLabel(note_scroll, text="No notes posted yet.", text_color="gray").pack(pady=20)
            else:
                for n in all_notes:
                    card = ctk.CTkFrame(note_scroll, fg_color="#34495e", corner_radius=8)
                    card.pack(fill="x", pady=5, padx=5)
                    header_txt = f"👤 {n.sender_name} ➔ [{n.target_role}] ({n.date})"
                    ctk.CTkLabel(card, text=header_txt, font=("Arial", 10, "bold"), text_color="#f1c40f",
                                 anchor="w").pack(fill="x", padx=10, pady=(5, 0))
                    ctk.CTkLabel(card, text=n.content, font=("Arial", 12), anchor="w", wraplength=430).pack(fill="x",
                                                                                                            padx=10,
                                                                                                            pady=(0, 5))

        refresh()

        bottom_bar = ctk.CTkFrame(board_win, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=10)

        depts = ["Waiter", "Barista", "Cashier", "Chef", "Cleaner"]
        dept_selector = ctk.CTkComboBox(bottom_bar, values=depts, width=110)
        dept_selector.pack(side="left", padx=5)

        note_input = ctk.CTkEntry(bottom_bar, placeholder_text="Type message...", width=250)
        note_input.pack(side="left", padx=5)

        def post():
            content = note_input.get().strip()
            target = dept_selector.get()
            if content:
                self.app.note_service.add_note(self.user.username, self.user.role, target, content)
                note_input.delete(0, 'end')
                refresh()

        ctk.CTkButton(bottom_bar, text="Post", width=70, command=post, fg_color="#2ecc71").pack(side="right", padx=5)