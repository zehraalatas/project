import json  # En üste eklemeyi unutma!
from models.gender import Gender
from models.role import Role
from models.cv import CV
import customtkinter as ctk


class ApplyScreen:
    def __init__(self, app):
        self.app = app
        self.gender_tool = Gender()
        self.role_tool = Role()
        self.experience_list = []  # Deneyimleri sakladığımız liste

        self.frame = ctk.CTkScrollableFrame(app, width=500, height=600, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        ctk.CTkLabel(self.frame, text="Detailed Job Application", font=("Arial", 22, "bold")).pack(pady=20)

        # --- Personal Info ---
        self.name = self.add_entry("First Name")
        self.surname = self.add_entry("Last Name")

        self.gender_combo = ctk.CTkComboBox(self.frame, values=self.gender_tool.get_all_values(), width=300,
                                            state="readonly")
        self.gender_combo.set("Select Gender")
        self.gender_combo.pack(pady=10)

        self.email = self.add_entry("Email Address")
        self.phone = self.add_entry("Phone Number")

        # --- Work Experience Section ---
        ctk.CTkLabel(self.frame, text="Work Experience", font=("Arial", 16, "bold"), text_color="#3498db").pack(
            pady=(20, 5))

        self.exp_company = self.add_entry("Company Name")
        self.exp_pos = self.add_entry("Position")
        self.exp_date = self.add_entry("Dates (e.g. 2020-2022)")

        # + Button (Validation dahil)
        self.add_exp_btn = ctk.CTkButton(self.frame, text="+ Add Experience", fg_color="#2980b9",
                                         command=self.add_experience_to_list)
        self.add_exp_btn.pack(pady=5)

        self.exp_count_lbl = ctk.CTkLabel(self.frame, text="No experiences added yet.", font=("Arial", 11),
                                          text_color="gray")
        self.exp_count_lbl.pack()

        # --- Role Selection ---
        available_roles = self.role_tool.get_employee_roles()
        self.role_combo = ctk.CTkComboBox(self.frame, values=available_roles, width=300, state="readonly")
        self.role_combo.set("Select Position")
        self.role_combo.pack(pady=20)

        # --- Footer Buttons ---
        ctk.CTkButton(self.frame, text="Submit CV", command=self.submit, fg_color="#2ecc71", text_color="black").pack(
            pady=10)
        ctk.CTkButton(self.frame, text="Back", fg_color="gray", command=self.app.show_login_screen).pack(pady=10)

        self.status_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

    def add_entry(self, placeholder):
        e = ctk.CTkEntry(self.frame, placeholder_text=placeholder, width=300)
        e.pack(pady=10)
        return e

    def add_experience_to_list(self):
        comp = self.exp_company.get().strip()
        pos = self.exp_pos.get().strip()
        date = self.exp_date.get().strip()

        # 1. Deneyim Alanları Boşluk Kontrolü
        if not comp or not pos or not date:
            self.show_error("Experience fields cannot be empty!")
            return

        # 2. Tarih Format Kontrolü (YYYY-YYYY)
        is_valid, error_msg = self.app.validation_service.is_valid_date_range(date)
        if not is_valid:
            self.show_error(error_msg)
            return

        # Listeye ekle
        self.experience_list.append({"company": comp, "pos": pos, "date": date})

        # Temizlik ve Bildirim
        self.exp_company.delete(0, 'end')
        self.exp_pos.delete(0, 'end')
        self.exp_date.delete(0, 'end')

        self.exp_count_lbl.configure(text=f"Total Experiences Added: {len(self.experience_list)}", text_color="#2ecc71")
        self.show_success("Experience added to list!")

    def submit(self):
        # 1. Verileri çek ve temizle
        n = self.name.get().strip()
        s = self.surname.get().strip()
        g = self.gender_combo.get()
        m = self.email.get().strip()
        p = self.phone.get().strip()
        r = self.role_combo.get()

        # 2. Temel Kişisel Bilgi Kontrolü
        if not n or not s or not m or not p:
            self.show_error("Please fill in all personal information!")
            return

        # 3. Seçim Kutusu Kontrolleri
        if g == "Select Gender":
            self.show_error("Please select your gender!")
            return
        if r == "Select Position":
            self.show_error("Please select the position!")
            return

        # 4. Email ve Telefon Format Kontrolü
        if not self.app.validation_service.is_valid_email(m):
            self.show_error("Invalid Email! (Must contain @ and .com)")
            return
        if not self.app.validation_service.is_valid_phone(p):
            self.show_error("Phone must start with 05 and be 11 digits!")
            return

        # 5. DENEYİM KONTROLÜ (Burayı güçlendirdik)
        # Kutularda herhangi bir yazı var mı diye bakıyoruz
        curr_c = self.exp_company.get().strip()
        curr_p = self.exp_pos.get().strip()
        curr_d = self.exp_date.get().strip()

        # Eğer kutulardan biri bile doluysa, kullanıcıyı '+' ya basması için zorluyoruz
        if curr_c or curr_p or curr_d:
            self.show_error("You have unsaved experience info! Click '+' to add it.")
            return

        # 6. Veriyi Hazırla
        import json
        if not self.experience_list:
            # Liste boşsa ve kutular da boşsa (yukarıdaki if'ten geçtiyse boş demektir)
            exp_final_data = "No Experience"
        else:
            # Liste doluysa JSON formatına çevir
            exp_final_data = json.dumps(self.experience_list, ensure_ascii=False)

        # 7. CV Nesnesini Oluştur ve Gönder
        from models.cv import CV
        new_cv = CV(n, s, g, m, p, exp_final_data, "")

        try:
            self.app.hr_service.submit_application(new_cv, r)
            self.show_success("Application submitted successfully!")
            # 1.5 saniye sonra login ekranına dön
            self.app.after(1500, self.app.show_login_screen)
        except Exception as e:
            self.show_error(f"Database Error: {str(e)}")

    def show_error(self, message):
        self.status_label.configure(text=message, text_color="#e74c3c")

    def show_success(self, message):
        self.status_label.configure(text=message, text_color="#2ecc71")