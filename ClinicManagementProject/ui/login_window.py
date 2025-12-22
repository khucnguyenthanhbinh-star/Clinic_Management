import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Frame giữa màn hình
        frame = ttk.Frame(self, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="ĐĂNG NHẬP", font=("Arial", 20, "bold"), foreground="#007bff").grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(frame, text="Tên đăng nhập:").grid(row=1, column=0, pady=10, sticky="e")
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid (row=1, column=1, pady=10, padx=5)
        self.username_entry.bind("<Return>", lambda event: self.handle_login())
        
        ttk.Label(frame, text="Mật khẩu:").grid(row=2, column=0, pady=10, sticky="e")
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=10, padx=5)
        self.password_entry.bind("<Return>", lambda event: self.handle_login())
        
        ttk.Button(frame, text="Đăng nhập", command=self.handle_login, width=20).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Link đăng ký
        lbl_reg = tk.Label(frame, text="Chưa có tài khoản? Đăng ký ngay", fg="blue", cursor="hand2")
        lbl_reg.grid(row=4, column=0, columnspan=2)
        lbl_reg.bind("<Button-1>", lambda e: self.show_register())

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, user = self.controller.auth.login(username, password)
        if success:
            self.controller.show_main_window()
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tên đăng nhập hoặc mật khẩu!")

    def show_register(self):
        self.destroy()
        RegisterWindow(self.master, self.controller)


class RegisterWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 20, "bold"), foreground="#28a745").grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username
        ttk.Label(frame, text="Tên đăng nhập:").grid(row=1, column=0, pady=10, sticky="e")
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=10, padx=5)
        
        # Password
        ttk.Label(frame, text="Mật khẩu:").grid(row=2, column=0, pady=10, sticky="e")
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=10, padx=5)
        
        # Confirm Password
        ttk.Label(frame, text="Nhập lại mật khẩu:").grid(row=3, column=0, pady=10, sticky="e")
        self.confirm_entry = ttk.Entry(frame, width=30, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=10, padx=5)
        
        # Ghi chú mật khẩu
        ttk.Label(frame, text="(Mật khẩu > 6 ký tự, gồm chữ và số)", font=("Arial", 8, "italic"), foreground="gray").grid(row=4, column=1, sticky="w")
        
        ttk.Button(frame, text="Đăng ký", command=self.handle_register, width=20).grid(row=5, column=0, columnspan=2, pady=20)
        
        lbl_login = tk.Label(frame, text="Đã có tài khoản? Đăng nhập", fg="blue", cursor="hand2")
        lbl_login.grid(row=6, column=0, columnspan=2)
        lbl_login.bind("<Button-1>", lambda e: self.go_back())

    def handle_register(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        cp = self.confirm_entry.get().strip()
        
        # Gọi hàm xử lý bên Auth
        success, msg = self.controller.auth.register(u, p, cp)
        
        if success:
            messagebox.showinfo("Thành công", msg)
            self.go_back()
        else:
            messagebox.showerror("Lỗi đăng ký", msg)

    def go_back(self):
        self.destroy()
        LoginWindow(self.master, self.controller)