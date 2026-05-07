import customtkinter as ctk


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

        query = "SELECT id, sender_name, request_type, detail, status FROM requests WHERE status='Pending Manager'"
        self.app.db_manager.cursor.execute(query)
        all_requests = self.app.db_manager.cursor.fetchall()

        if not all_requests:
            ctk.CTkLabel(self.request_tab, text="No pending requests found.",
                         font=("Arial", 14), text_color="gray").pack(pady=40)
            return

        scroll_view = ctk.CTkScrollableFrame(self.request_tab, fg_color="transparent")
        scroll_view.pack(fill="both", expand=True, pady=10)

        type_labels = {"Leave": "Leave Request", "Salary": "Salary Raise"}

        for req in all_requests:
            r_id, sender, r_type, info, status = req
            row_frame = ctk.CTkFrame(scroll_view)
            row_frame.pack(pady=5, padx=20, fill="x")

            icon = "📅" if r_type == "Leave" else "💰"
            eng_type = type_labels.get(r_type, r_type)
            display_text = f"{icon} {sender.capitalize()} - {eng_type} ({info})"

            ctk.CTkLabel(row_frame, text=display_text, font=("Arial", 13, "bold")).pack(side="left", padx=20, pady=10)

            ctk.CTkButton(row_frame, text="Approve ✅", width=110, fg_color="#3498db",
                          command=lambda i=r_id, s=sender, rt=r_type: self.update_request(i, "Approved", s, rt)).pack(
                side="right", padx=10)

            ctk.CTkButton(row_frame, text="Reject ❌", width=90, fg_color="#e74c3c",
                          command=lambda i=r_id, s=sender, rt=r_type: self.update_request(i, "Rejected", s, rt)).pack(
                side="right", padx=10)

    def update_request(self, req_id, new_status, employee_name, req_type):
        """Handles the decision and sends notification based on new English schema"""
        success = self.app.hr_service.update_request_status(req_id, new_status, "Manager")

        if success:
            display_type = "Leave" if req_type == "Leave" else "Salary Raise"

            if new_status == "Approved":
                msg = f"Your {display_type} request was approved by the Manager, waiting for Boss. ⏳"
            else:
                msg = f"Your {display_type} request was rejected by the Manager. ❌"

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
        self.btn_notif = ctk.CTkButton(self.profile_tab, text="🔔 Notifications", command=self.show_notifications,
                                       fg_color="#34495e", width=380, height=35)
        self.btn_notif.pack(pady=5)

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

            ctk.CTkLabel(day_card, text=status_text, font=("Arial", 13, "bold"), text_color="white").place(relx=0.5,
                                                                                                           rely=0.5,
                                                                                                           anchor="center")

        # BURASI SENİN KAYBOLAN BUTONLARININ YERİ (Manager's own requests)
        action_row = ctk.CTkFrame(self.profile_tab, fg_color="transparent")
        action_row.pack(pady=35)

        ctk.CTkButton(action_row, text="Request Leave", fg_color="#f39c12", width=150, height=40,
                      command=lambda: self.make_own_request("Leave")).pack(side="left", padx=15)

        ctk.CTkButton(action_row, text="Request Raise", fg_color="#8e44ad", width=150, height=40,
                      command=lambda: self.make_own_request("Salary")).pack(side="left", padx=15)

        self.refresh_notif_badge()

    def refresh_notif_badge(self):
        """Updates the notification button text if there are new messages"""
        unread_list = self.app.notification_service.get_unread(self.user.username)
        if len(unread_list) > 0:
            self.btn_notif.configure(text=f"🔔 Notifications ({len(unread_list)})", fg_color="#e67e22")
        else:
            self.btn_notif.configure(text="🔔 Notifications", fg_color="#34495e")

    def show_notifications(self):
        """Opens a window to see all unread messages with a scrollable view"""
        unread_items = self.app.notification_service.get_unread(self.user.username)
        notif_window = ctk.CTkToplevel(self.app)
        notif_window.title("Manager Notifications")
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

    def make_own_request(self, req_type):
        """Handles Manager's own leave and salary requests directly to Boss. Allows updating."""

        self.app.db_manager.cursor.execute(
            "SELECT id, detail FROM requests WHERE sender_name=? AND request_type=? AND status='Pending Boss'",
            (self.user.username, req_type)
        )
        existing_req = self.app.db_manager.cursor.fetchone()

        req_win = ctk.CTkToplevel(self.app)
        display_title = "Leave" if req_type == "Leave" else "Salary Raise"
        req_win.geometry("300x260")
        req_win.grab_set()
        req_win.attributes("-topmost", True)

        if existing_req:
            req_win.title(f"Update Pending {display_title}")
            ctk.CTkLabel(req_win, text="⚠️ You already have a pending request!", text_color="#f39c12",
                         font=("Arial", 12, "bold")).pack(pady=(15, 0))
            ctk.CTkLabel(req_win, text="Waiting for Boss approval.", text_color="gray", font=("Arial", 11)).pack(
                pady=(0, 5))
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
                self.app.hr_service.submit_manager_request(self.user.username, req_type, detail)

            req_win.destroy()

        color = "#f39c12" if req_type == "Leave" else "#8e44ad"
        btn_text = "Update Request" if existing_req else "Send Request"

        ctk.CTkButton(req_win, text=btn_text, command=submit_action, fg_color=color).pack(pady=15)

    def open_all_boards(self):
        """Board to communicate with all department staff"""
        board_win = ctk.CTkToplevel(self.app)
        board_win.title("Global Communication Board")
        board_win.geometry("500x600")
        board_win.grab_set()

        ctk.CTkLabel(board_win, text="📝 Departmental Communication", font=("Arial", 18, "bold")).pack(pady=10)

        # --- YENİ EKLENEN FİLTRE ALANI ---
        filter_frame = ctk.CTkFrame(board_win, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(filter_frame, text="Filter by Target:", font=("Arial", 12, "bold")).pack(side="left", padx=(5, 10))

        roles = ["All", "Waiter", "Barista", "Cashier", "Chef", "Cleaner"]
        filter_combo = ctk.CTkComboBox(filter_frame, values=roles, width=130, state="readonly",
                                       command=lambda e: refresh())
        filter_combo.set("All")
        filter_combo.pack(side="left")
        # ---------------------------------

        note_scroll = ctk.CTkScrollableFrame(board_win, fg_color="#2c3e50")
        note_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        def refresh(*args):
            for child in note_scroll.winfo_children():
                child.destroy()

            all_notes = self.app.note_service.get_notes_for_user(self.user.role)
            selected_filter = filter_combo.get()

            has_notes = False
            if all_notes:
                for n in all_notes:
                    # Filtreleme mantığı
                    if selected_filter != "All" and n.target_role != selected_filter:
                        continue

                    has_notes = True
                    card = ctk.CTkFrame(note_scroll, fg_color="#34495e", corner_radius=8)
                    card.pack(fill="x", pady=5, padx=5)
                    header_txt = f"👤 {n.sender_name} ➔ [{n.target_role}] ({n.date})"
                    ctk.CTkLabel(card, text=header_txt, font=("Arial", 10, "bold"), text_color="#f1c40f",
                                 anchor="w").pack(fill="x", padx=10, pady=(5, 0))
                    ctk.CTkLabel(card, text=n.content, font=("Arial", 12), anchor="w", wraplength=430).pack(fill="x",
                                                                                                            padx=10,
                                                                                                            pady=(0, 5))
            if not has_notes:
                ctk.CTkLabel(note_scroll, text="No notes found for this filter.", text_color="gray").pack(pady=20)

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