import tkinter as tk
from tkinter import messagebox
from db import Database
from controllers import Controller
from views_patient import PatientViewManager
from views_doctor import DoctorViewManager
from views_admin import AdminViewManager

class ClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Quản lý Phòng khám")
        self.geometry("1000x700")
        
        self.db = Database()
        self.controller = Controller(self.db)
        self.current_user_id = None
        
        self.show_login()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.config(menu="") # Clear menu bar

    def add_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        menubar.add_command(label="Đăng xuất", command=self.logout)

    def logout(self):
        self.current_user_id = None
        self.show_login()

    def show_login(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="ĐĂNG NHẬP", font=("Arial", 24, "bold"), fg="#333").pack(pady=30)
        
        tk.Label(frame, text="Tên đăng nhập:", font=("Arial", 11)).pack(anchor='w', padx=20)
        entry_user = tk.Entry(frame, font=("Arial", 12), width=40)
        entry_user.pack(pady=5, ipady=3, padx=20)

        tk.Label(frame, text="Mật khẩu:", font=("Arial", 11)).pack(anchor='w', padx=20, pady=(10, 0))
        entry_pass = tk.Entry(frame, show="*", font=("Arial", 12), width=40)
        entry_pass.pack(pady=5, ipady=3, padx=20)

        def login_action():
            user = self.controller.login(entry_user.get(), entry_pass.get())
            if user:
                self.current_user_id = user[0]
                role = user[1]
                if role == 'patient': self.show_patient_dashboard()
                elif role == 'doctor': self.show_doctor_dashboard()
                elif role == 'admin': self.show_admin_dashboard()
            else:
                messagebox.showerror("Lỗi", "Sai thông tin đăng nhập")

        tk.Button(frame, text="Đăng nhập", font=("Arial", 12, "bold"), bg="#2196F3", fg="white", width=38, command=login_action).pack(pady=20, padx=20)
        tk.Button(frame, text="Đăng ký (Bệnh nhân)", font=("Arial", 10), fg="blue", relief="flat", command=self.show_register).pack(pady=5)

    def show_register(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text="ĐĂNG KÝ", font=("Arial", 20, "bold")).pack(pady=20)
        entries = {}
        for field in ["Họ tên", "Email", "SĐT", "Mật khẩu"]:
            tk.Label(frame, text=field).pack(anchor='w', padx=20)
            e = tk.Entry(frame, width=40, show="*" if field == "Mật khẩu" else None)
            e.pack(pady=5, padx=20)
            entries[field] = e

        def reg():
            success, msg = self.controller.register_patient(entries["SĐT"].get(), entries["Email"].get(), entries["Mật khẩu"].get(), entries["Họ tên"].get())
            if success: messagebox.showinfo("OK", msg); self.show_login()
            else: messagebox.showerror("Lỗi", msg)

        tk.Button(frame, text="Đăng ký", bg="#4CAF50", fg="white", width=38, command=reg).pack(pady=20)
        tk.Button(frame, text="Quay lại", command=self.show_login).pack()

    # --- Orchestration Methods ---
    def show_patient_dashboard(self):
        self.clear_frame()
        self.add_menu()
        
        notebook = tk.ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)
        manager = PatientViewManager(self, self.controller, self.current_user_id)

        tabs = [("Thông tin", manager.build_patient_info_tab),
                ("Lịch hẹn", manager.build_patient_appt_tab),
                ("Hồ sơ", manager.build_patient_records_tab),
                ("Thanh toán", manager.build_patient_payment_tab),
                ("Thông báo", manager.build_notif_tab)]
        
        for name, func in tabs:
            frame = tk.Frame(notebook)
            notebook.add(frame, text=name)
            func(frame)

    def show_doctor_dashboard(self):
        manager = DoctorViewManager(self, self.controller, self.current_user_id)
        manager.show_dashboard()

    def show_admin_dashboard(self):
        manager = AdminViewManager(self, self.controller)
        manager.show_dashboard()

if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()