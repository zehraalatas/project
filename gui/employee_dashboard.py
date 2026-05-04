import customtkinter as ctk
import datetime
from models.schedule import Schedule


class EmployeeDashboard:
    def __init__(self, app):
        self.app = app
        self.user = self.app.current_user

        # Managing work schedule via model
        self.user_schedule = Schedule(self.user.user_id, self.user.off_day)

        # --- Top Info Panel ---
        # capitalize() used for name formatting
        self.header = ctk.CTkLabel(app, text=f"☕ Welcome {self.user.username.capitalize()}",
                                   font=("Arial", 26, "bold"))
        self.header.pack(pady=(30, 10))

        # Using a simple string for role and salary info
        display_text = f"Role: {self.user.role} | Salary: {self.user.salary} ₺"
        self.role_info = ctk.CTkLabel(app, text=display_text,
                                      font=("Arial", 14), text_color="gray")
        self.role_info.pack(pady=5)

        # --- Main Action Buttons ---
        self.btn_notif = ctk.CTkButton(app, text="🔔 Notifications", command=self.show_notifications,
                                       width=280, height=40, fg_color="#2c3e50")
        self.btn_notif.pack(pady=10)

        self.btn_board = ctk.CTkButton(app, text="📝 Department Board", command=self.open_notice_board,
                                       width=280, height=40, fg_color="#8e44ad")
        self.btn_board.pack(pady=10)

        # --- Automatic Status Check ---
        # Get today's name from our list in Schedule model
        day_index = datetime.datetime.today().weekday()
        today_name = self.user_schedule.DAYS[day_index]

        # Logic: If today is off day, status is 'Off', else 'Working'
        if today_name.lower() == self.user.off_day.lower():
            current_status = "Off Day"
        else:
            current_status = "Working"

        # Logging status to database via HR service
        self.app.hr_service.log_status(self.user.user_id, self.user.username, current_status)

        # --- Weekly Schedule Section ---
        self.calendar_frame = ctk.CTkFrame(app, corner_radius=10)
        self.calendar_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(self.calendar_frame, text="📅 Your Weekly Schedule", font=("Arial", 16, "bold")).pack(pady=10)

        self.grid_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        self.grid_frame.pack(pady=10)

        # Get total staff for this role to check permission
        self.app.db_manager.cursor.execute(
            "SELECT COUNT(*) FROM users WHERE role=?", (self.user.role,)
        )
        staff_count = self.app.db_manager.cursor.fetchone()[0]

        # Calendar Loop - Creating boxes for each day
        for i, day in enumerate(self.user_schedule.DAYS):
            short_name = day[:3]  # Mon, Tue, etc.
            ctk.CTkLabel(self.grid_frame, text=short_name, font=("Arial", 12, "bold"), width=70).grid(
                row=0, column=i, padx=5, pady=5)

            # Determine color and text based on role count and off day
            if staff_count <= 1:
                box_text = "No Off"
                box_color = "#7f8c8d"
            elif day == self.user.off_day:
                box_text = "OFF"
                box_color = "#e74c3c"
            else:
                box_text = "Work"
                box_color = "#2ecc71"

            day_box = ctk.CTkFrame(self.grid_frame, width=75, height=55, fg_color=box_color, corner_radius=5)
            day_box.grid(row=1, column=i, padx=5, pady=5)
            day_box.grid_propagate(False)

            status_lbl = ctk.CTkLabel(day_box, text=box_text, font=("Arial", 11, "bold"), text_color="white")
            status_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # --- Request Buttons ---
        self.request_area = ctk.CTkFrame(app, fg_color="transparent")
        self.request_area.pack(pady=10)

        if staff_count <= 1:
            ctk.CTkButton(
                self.request_area, text="Day Off (Locked)",
                width=160, height=40, fg_color="gray", state="disabled"
            ).grid(row=0, column=0, padx=10)
        else:
            ctk.CTkButton(self.request_area, text="Request Off", command=lambda: self.make_request("Day Off"),
                          width=140, height=40, fg_color="#f39c12").grid(row=0, column=0, padx=10)

        ctk.CTkButton(self.request_area, text="Request Raise", command=lambda: self.make_request("Salary Raise"),
                      width=140, height=40, fg_color="#8e44ad").grid(row=0, column=1, padx=10)

        # --- Bottom Menu ---
        self.footer = ctk.CTkFrame(app, fg_color="transparent")
        self.footer.pack(side="bottom", pady=25)

        self.btn_settings = ctk.CTkButton(self.footer, text="⚙️ Settings", command=self.open_settings,
                                          fg_color="#34495e", width=110)
        self.btn_settings.grid(row=0, column=0, padx=10)

        self.btn_logout = ctk.CTkButton(self.footer, text="Logout", command=self.app.show_login_screen,
                                        fg_color="darkred", width=110)
        self.btn_logout.grid(row=0, column=1, padx=10)

        self.refresh_notif_badge()

    def refresh_notif_badge(self):
        """Updates the notification button text if there are new messages"""
        unread_list = self.app.notification_service.get_unread(self.user.username)
        if len(unread_list) > 0:
            self.btn_notif.configure(text=f"🔔 Notifications ({len(unread_list)})", fg_color="#e67e22")
        else:
            self.btn_notif.configure(text="🔔 Notifications", fg_color="#2c3e50")

    def show_notifications(self):
        """Opens a window to see all unread messages"""
        unread_items = self.app.notification_service.get_unread(self.user.username)
        notif_window = ctk.CTkToplevel(self.app)
        notif_window.title("Your Notifications")
        notif_window.geometry("350x300")
        notif_window.grab_set()

        if not unread_items:
            ctk.CTkLabel(notif_window, text="No new messages 📭", text_color="gray").pack(pady=40)
        else:
            for item in unread_items:
                ctk.CTkLabel(notif_window, text=f"• {item.message}", wraplength=300).pack(pady=8, padx=20)

            def mark_as_read():
                self.app.notification_service.mark_all_read(self.user.username)
                self.refresh_notif_badge()
                notif_window.destroy()

            ctk.CTkButton(notif_window, text="Mark All as Read", command=mark_as_read, fg_color="#3498db").pack(pady=15)

    def make_request(self, req_type):
        """Handles leave and salary increase requests"""
        req_win = ctk.CTkToplevel(self.app)
        req_win.title(f"{req_type} Request")
        req_win.geometry("300x220")
        req_win.grab_set()
        req_win.attributes("-topmost", True)

        user_input = None

        if req_type == "Day Off":
            ctk.CTkLabel(req_win, text="Select day for leave:", font=("Arial", 13, "bold")).pack(pady=(20, 5))
            # List for ComboBox
            days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            user_input = ctk.CTkComboBox(req_win, values=days_list, width=180, state="readonly")
            user_input.set("Select Day")
            user_input.pack(pady=10)
        else:
            ctk.CTkLabel(req_win, text="Enter details (e.g. 10%):", font=("Arial", 13, "bold")).pack(pady=(20, 5))
            user_input = ctk.CTkEntry(req_win, placeholder_text="Explain here...", width=200)
            user_input.pack(pady=10)

        def submit_to_manager():
            # Dictionary to pack request details (Lesson Topic: Dictionary)
            detail = user_input.get()

            if req_type == "Day Off" and detail == "Select Day":
                return
            if not detail.strip():
                return

            request_data = {
                "user": self.user.username,
                "type": req_type,
                "info": detail
            }

            # Send to HR service
            self.app.hr_service.submit_internal_request(request_data["user"], request_data["type"],
                                                        request_data["info"])

            # Local notification
            msg = f"✅ Your {req_type} request has been sent to Manager!"
            self.app.notification_service.send(self.user.username, msg)

            req_win.destroy()

        color = "#f39c12" if req_type == "Day Off" else "#8e44ad"
        ctk.CTkButton(req_win, text="Send Request", command=submit_to_manager, fg_color=color).pack(pady=15)

    def open_settings(self):
        """Window to update username and password"""
        set_win = ctk.CTkToplevel(self.app)
        set_win.title("Account Settings")
        set_win.geometry("350x400")
        set_win.grab_set()

        ctk.CTkLabel(set_win, text="⚙️ Update Credentials", font=("Arial", 18, "bold")).pack(pady=20)

        name_entry = ctk.CTkEntry(set_win, placeholder_text="New Username", width=250)
        name_entry.insert(0, self.user.username)
        name_entry.pack(pady=10)

        pass_entry = ctk.CTkEntry(set_win, placeholder_text="New Password", show="*", width=250)
        pass_entry.pack(pady=10)

        msg_label = ctk.CTkLabel(set_win, text="", font=("Arial", 11, "bold"))
        msg_label.pack(pady=5)

        def save_changes():
            u = name_entry.get().strip()
            p = pass_entry.get().strip()

            if not u or not p:
                msg_label.configure(text="Fields cannot be empty!", text_color="#e74c3c")
                return

            # Update via auth service
            done, info = self.app.auth_service.update_credentials(self.user.user_id, u, p)

            if done:
                msg_label.configure(text=info, text_color="#2ecc71")
                self.user.username = u
                self.header.configure(text=f"☕ Welcome {u.capitalize()}")
                set_win.after(1500, set_win.destroy)
            else:
                msg_label.configure(text=info, text_color="#e74c3c")

        ctk.CTkButton(set_win, text="Save Settings", command=save_changes, fg_color="#3498db").pack(pady=15)

    def open_notice_board(self):
        """Shared board for department communication"""
        board_win = ctk.CTkToplevel(self.app)
        board_win.title(f"{self.user.role} Board")
        board_win.geometry("450x500")
        board_win.grab_set()

        ctk.CTkLabel(board_win, text=f"📝 {self.user.role} Communication Board", font=("Arial", 18, "bold")).pack(
            pady=10)

        # Scrollable area for notes
        note_scroll = ctk.CTkScrollableFrame(board_win, fg_color="#2c3e50")
        note_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def load_board_messages():
            # Function to refresh the notes
            for child in note_scroll.winfo_children():
                child.destroy()

            # Fetching notes based on role (using a list of objects)
            all_notes = self.app.note_service.get_notes_for_user(self.user.role)

            if not all_notes:
                ctk.CTkLabel(note_scroll, text="No notes yet.", text_color="gray").pack(pady=20)
            else:
                for n in all_notes:
                    frame = ctk.CTkFrame(note_scroll, fg_color="#34495e", corner_radius=5)
                    frame.pack(fill="x", pady=5, padx=5)

                    header_text = f"👤 {n.sender_name} ({n.date})"
                    ctk.CTkLabel(frame, text=header_text, font=("Arial", 10, "bold"),
                                 text_color="#f1c40f", anchor="w").pack(fill="x", padx=10, pady=(5, 0))

                    ctk.CTkLabel(frame, text=n.content, font=("Arial", 12), anchor="w", wraplength=380).pack(
                        fill="x", padx=10, pady=(0, 5))

        load_board_messages()

        # Write new note area
        write_frame = ctk.CTkFrame(board_win, fg_color="transparent")
        write_frame.pack(fill="x", padx=10, pady=10)

        note_input = ctk.CTkEntry(write_frame, placeholder_text="Type a note...", width=300)
        note_input.pack(side="left", padx=5)

        def post_note():
            txt = note_input.get().strip()
            if txt:
                # Add note using our service
                self.app.note_service.add_note(self.user.username, self.user.role, self.user.role, txt)
                note_input.delete(0, 'end')
                load_board_messages()

        ctk.CTkButton(write_frame, text="Post", width=80, command=post_note, fg_color="#2ecc71").pack(side="right",
                                                                                                      padx=5)