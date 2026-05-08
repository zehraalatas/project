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
        self.header = ctk.CTkLabel(app, text=f"☕ Welcome {self.user.get_display_name()}",
                                   font=("Arial", 26, "bold"))
        self.header.pack(pady=(30, 10))

        # 2 basamaklı maaş gösterimi (Örn: 15000.00)
        display_text = f"Role: {self.user.role} | Salary: {self.user.salary:.2f} ₺"
        self.role_info = ctk.CTkLabel(app, text=display_text, font=("Arial", 14), text_color="gray")
        self.role_info.pack(pady=5)

        # --- Main Action Buttons ---
        self.btn_notif = ctk.CTkButton(app, text="🔔 Notifications", command=self.show_notifications,
                                       width=280, height=40, fg_color="#2c3e50")
        self.btn_notif.pack(pady=10)

        self.btn_board = ctk.CTkButton(app, text="📝 Department Board", command=self.open_notice_board,
                                       width=280, height=40, fg_color="#8e44ad")
        self.btn_board.pack(pady=10)

        # --- Automatic Status Check ---
        day_index = datetime.datetime.today().weekday()
        today_name = self.user_schedule.DAYS[day_index]

        if today_name.lower() == self.user.off_day.lower():
            current_status = "Off Day"
        else:
            current_status = "Working"

        self.app.hr_service.log_status(self.user.user_id, self.user.username, current_status)

        # --- Weekly Schedule Section ---
        self.calendar_frame = ctk.CTkFrame(app, corner_radius=10)
        self.calendar_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(self.calendar_frame, text="📅 Your Weekly Schedule", font=("Arial", 16, "bold")).pack(pady=10)

        self.grid_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        self.grid_frame.pack(pady=10)

        self.app.db_manager.cursor.execute("SELECT COUNT(*) FROM users WHERE role=?", (self.user.role,))
        staff_count = self.app.db_manager.cursor.fetchone()[0]

        for i, day in enumerate(self.user_schedule.DAYS):
            short_name = day[:3]
            ctk.CTkLabel(self.grid_frame, text=short_name, font=("Arial", 12, "bold"), width=70).grid(
                row=0, column=i, padx=5, pady=5)

            if not self.user.can_request_leave(staff_count):
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

        if not self.user.can_request_leave(staff_count):
            ctk.CTkButton(self.request_area, text="Day Off (Locked)", width=160, height=40, fg_color="gray",
                          state="disabled").grid(row=0, column=0, padx=10)
        else:
            ctk.CTkButton(self.request_area, text="Request Off", command=lambda: self.make_request("Leave"), width=140,
                          height=40, fg_color="#f39c12").grid(row=0, column=0, padx=10)

        ctk.CTkButton(self.request_area, text="Request Raise", command=lambda: self.make_request("Salary"), width=140,
                      height=40, fg_color="#8e44ad").grid(row=0, column=1, padx=10)

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
        unread_list = self.app.notification_service.get_unread(self.user.username)
        if len(unread_list) > 0:
            self.btn_notif.configure(text=f"🔔 Notifications ({len(unread_list)})", fg_color="#e67e22")
        else:
            self.btn_notif.configure(text="🔔 Notifications", fg_color="#2c3e50")

    def show_notifications(self):
        unread_items = self.app.notification_service.get_unread(self.user.username)
        notif_window = ctk.CTkToplevel(self.app)
        notif_window.title("Your Notifications")
        notif_window.geometry("400x350")
        notif_window.grab_set()

        if not unread_items:
            ctk.CTkLabel(notif_window, text="No new messages 📭", text_color="gray").pack(pady=40)
        else:
            scroll_frame = ctk.CTkScrollableFrame(notif_window, fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

            for item in unread_items:
                notif_box = ctk.CTkFrame(scroll_frame, fg_color="#34495e", corner_radius=5)
                notif_box.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(notif_box, text=f"• {item.message}", wraplength=320, justify="left").pack(pady=10, padx=10,
                                                                                                       anchor="w")

            def mark_as_read():
                self.app.notification_service.mark_all_read(self.user.username)
                self.refresh_notif_badge()
                notif_window.destroy()

            ctk.CTkButton(notif_window, text="Mark All as Read", command=mark_as_read, fg_color="#3498db").pack(
                side="bottom", pady=15)

    def make_request(self, req_type):
        """Handles leave and salary increase requests, blocking/updating based on Manager status."""
        self.app.db_manager.cursor.execute(
            "SELECT id, detail, status FROM requests WHERE sender_name=? AND request_type=? AND status IN ('Pending Manager', 'Pending Boss')",
            (self.user.username, req_type)
        )
        existing_req = self.app.db_manager.cursor.fetchone()

        req_win = ctk.CTkToplevel(self.app)
        display_title = "Leave" if req_type == "Leave" else "Salary Raise"
        req_win.geometry("300x260")
        req_win.grab_set()
        req_win.attributes("-topmost", True)

        # 1. Kilitli Durum (Patrona ulaştıysa)
        if existing_req and existing_req[2] == "Pending Boss":
            req_win.title("Request Locked")
            ctk.CTkLabel(req_win, text="🔒 Request Locked", text_color="#e74c3c", font=("Arial", 16, "bold")).pack(
                pady=(30, 10))
            ctk.CTkLabel(req_win, text="Manager approved this request.\nWaiting for Boss approval.", text_color="gray",
                         font=("Arial", 12)).pack(pady=10)
            ctk.CTkButton(req_win, text="Close", command=req_win.destroy, fg_color="#34495e").pack(pady=20)
            return

        # 2. Müdürde Bekleyen veya Yeni Talep
        if existing_req:
            req_win.title(f"Update Pending {display_title}")
            ctk.CTkLabel(req_win, text="⚠️ You have a pending request!", text_color="#f39c12",
                         font=("Arial", 12, "bold")).pack(pady=(15, 0))
            ctk.CTkLabel(req_win, text="You can update it below:", font=("Arial", 13, "bold")).pack(pady=(10, 5))
        else:
            req_win.title(f"New {display_title} Request")
            prompt_text = "Select day for leave:" if req_type == "Leave" else "Enter details (e.g. 10%):"
            ctk.CTkLabel(req_win, text=prompt_text, font=("Arial", 13, "bold")).pack(pady=(20, 5))

        user_input = None
        if req_type == "Leave":
            days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            user_input = ctk.CTkComboBox(req_win, values=days_list, width=180, state="readonly")
            if existing_req:
                user_input.set(existing_req[1])
            else:
                user_input.set("Select Day")
            user_input.pack(pady=10)
        else:
            user_input = ctk.CTkEntry(req_win, placeholder_text="Explain here...", width=200)
            if existing_req:
                user_input.insert(0, existing_req[1])
            user_input.pack(pady=10)

        def submit_action():
            detail = user_input.get()
            if req_type == "Leave" and detail == "Select Day": return
            if not detail.strip(): return

            if existing_req:
                req_id = existing_req[0]
                self.app.db_manager.cursor.execute("UPDATE requests SET detail=? WHERE id=?", (detail, req_id))
                self.app.db_manager.conn.commit()
            else:
                self.app.hr_service.submit_internal_request(self.user.username, req_type, detail)

            req_win.destroy()

        color = "#f39c12" if req_type == "Leave" else "#8e44ad"
        btn_text = "Update Request" if existing_req else "Send Request"

        # SADECE 1 TANE BUTON VAR!
        ctk.CTkButton(req_win, text=btn_text, command=submit_action, fg_color=color).pack(pady=15)

    def open_settings(self):
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
            done, info = self.app.auth_service.update_credentials(self.user.user_id, u, p)
            if done:
                msg_label.configure(text=info, text_color="#2ecc71")
                self.user.username = u
                self.header.configure(text=f"☕ Welcome {self.user.get_display_name()}")
                set_win.after(1500, set_win.destroy)
            else:
                msg_label.configure(text=info, text_color="#e74c3c")

        ctk.CTkButton(set_win, text="Save Settings", command=save_changes, fg_color="#3498db").pack(pady=15)

    def open_notice_board(self):
        board_win = ctk.CTkToplevel(self.app)
        board_win.title(f"{self.user.role} Board")
        board_win.geometry("450x500")
        board_win.grab_set()

        ctk.CTkLabel(board_win, text=f"📝 {self.user.role} Communication Board", font=("Arial", 18, "bold")).pack(
            pady=10)
        note_scroll = ctk.CTkScrollableFrame(board_win, fg_color="#2c3e50")
        note_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def load_board_messages():
            for child in note_scroll.winfo_children(): child.destroy()
            all_notes = self.app.note_service.get_notes_for_user(self.user.role)
            if not all_notes:
                ctk.CTkLabel(note_scroll, text="No notes yet.", text_color="gray").pack(pady=20)
            else:
                for n in all_notes:
                    frame = ctk.CTkFrame(note_scroll, fg_color="#34495e", corner_radius=5)
                    frame.pack(fill="x", pady=5, padx=5)
                    header_text = f"👤 {n.sender_name} ({n.date})"
                    ctk.CTkLabel(frame, text=header_text, font=("Arial", 10, "bold"), text_color="#f1c40f",
                                 anchor="w").pack(fill="x", padx=10, pady=(5, 0))
                    ctk.CTkLabel(frame, text=n.content, font=("Arial", 12), anchor="w", wraplength=380).pack(fill="x",
                                                                                                             padx=10,
                                                                                                             pady=(0,
                                                                                                                   5))

        load_board_messages()

        write_frame = ctk.CTkFrame(board_win, fg_color="transparent")
        write_frame.pack(fill="x", padx=10, pady=10)
        note_input = ctk.CTkEntry(write_frame, placeholder_text="Type a note...", width=300)
        note_input.pack(side="left", padx=5)

        def post_note():
            txt = note_input.get().strip()
            if txt:
                self.app.note_service.add_note(self.user.username, self.user.role, self.user.role, txt)
                note_input.delete(0, 'end')
                load_board_messages()

        ctk.CTkButton(write_frame, text="Post", width=80, command=post_note, fg_color="#2ecc71").pack(side="right",
                                                                                                      padx=5)