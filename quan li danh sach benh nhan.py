import tkinter as tk
from tkinter import ttk, messagebox

class ClinicManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Phòng khám")
        self.root.geometry("800x600")
        
        # Dữ liệu mẫu (bệnh nhân)
        self.users = {
            "admin": {"password": "admin", "role": "admin", "name": "Admin"},
            "bs1": {"password": "123", "role": "doctor", "name": "BS. Nguyễn Văn A"},
            "bn1": {"password": "123", "role": "patient", "name": "Nguyễn Thị B", "info": {}},
            "bn2": {"password": "123", "role": "patient", "name": "Trần Văn C", "info": {}}
        }

        self.current_user = None
        self.current_role = None
        
        self.create_login_screen()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_login_screen(self):
        self.clear_screen()
        
        frame = ttk.Frame(self.root, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text="ĐĂNG NHẬP", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(frame, text="Tên đăng nhập:").grid(row=1, column=0, pady=10, sticky="e")
        username_entry = ttk.Entry(frame, width=25)
        username_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Mật khẩu:").grid(row=2, column=0, pady=10, sticky="e")
        password_entry = ttk.Entry(frame, width=25, show="*")
        password_entry.grid(row=2, column=1, pady=10)
        
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            if username in self.users and self.users[username]["password"] == password:
                self.current_user = username
                self.current_role = self.users[username]["role"]
                self.create_main_screen()
            else:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")
        
        ttk.Button(frame, text="Đăng nhập", command=login).grid(row=3, column=0, columnspan=2, pady=20)
    
    def create_main_screen(self):
        self.clear_screen()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Xin chào: {self.users[self.current_user]['name']}", 
                 font=("Arial", 12)).pack(side="left")
        ttk.Button(top_frame, text="Đăng xuất", command=self.create_login_screen).pack(side="right")
        
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Menu
        menu_frame = ttk.LabelFrame(container, text="Menu", width=200)
        menu_frame.pack(side="left", fill="y", padx=5)
        menu_frame.pack_propagate(False)
        
        # Content
        self.content_frame = ttk.Frame(container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Tạo menu theo role
        if self.current_role == "admin":
            self.create_admin_menu(menu_frame)
        else:
            messagebox.showinfo("Thông báo", "Bạn không có quyền truy cập vào phần này.")

    def create_admin_menu(self, parent):
        ttk.Button(parent, text="Quản lý bệnh nhân", command=self.show_patient_management).pack(fill="x", pady=2)
    
    def show_patient_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="QUẢN LÝ BỆNH NHÂN", font=("Arial", 16, "bold")).pack(pady=20)
        
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        # Treeview to show patients' details
        tree = ttk.Treeview(tree_frame, columns=("username", "name", "info"), show="headings")
        tree.heading("username", text="Tên đăng nhập")
        tree.heading("name", text="Họ tên")
        tree.heading("info", text="Thông tin")
        
        # Fill treeview with patient data
        for username, user in self.users.items():
            if user["role"] == "patient":
                tree.insert("", "end", values=(username, user["name"], str(user["info"])))
        
        tree.pack(fill="both", expand=True)

        # Button to add new patient
        ttk.Button(self.content_frame, text="Thêm bệnh nhân", command=self.show_add_patient_form).pack(pady=20)
    
    def show_add_patient_form(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="THÊM BỆNH NHÂN", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Tên đăng nhập:").grid(row=0, column=0, pady=10, sticky="e")
        username_entry = ttk.Entry(frame, width=25)
        username_entry.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Mật khẩu:").grid(row=1, column=0, pady=10, sticky="e")
        password_entry = ttk.Entry(frame, width=25, show="*")
        password_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Họ tên:").grid(row=2, column=0, pady=10, sticky="e")
        name_entry = ttk.Entry(frame, width=25)
        name_entry.grid(row=2, column=1, pady=10)
        
        ttk.Label(frame, text="Thông tin bệnh nhân:").grid(row=3, column=0, pady=10, sticky="e")
        info_entry = ttk.Entry(frame, width=25)
        info_entry.grid(row=3, column=1, pady=10)
        
        def add_patient():
            username = username_entry.get()
            password = password_entry.get()
            name = name_entry.get()
            info = info_entry.get()
            
            if username and password and name and info:
                if username not in self.users:
                    self.users[username] = {"password": password, "role": "patient", "name": name, "info": info}
                    messagebox.showinfo("Thành công", "Đã thêm bệnh nhân!")
                    self.show_patient_management()  # Refresh patient management screen
                else:
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
        
        ttk.Button(frame, text="Thêm bệnh nhân", command=add_patient).grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Quay lại", command=self.show_patient_management).grid(row=5, column=0, columnspan=2)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicManagementSystem(root)
    root.mainloop()
