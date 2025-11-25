import tkinter as tk
from tkinter import ttk, messagebox

class ClinicManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Phòng khám")
        self.root.geometry("800x600")
        
        # Dữ liệu mẫu (bệnh nhân và bác sĩ)
        self.users = {
            "admin": {"password": "admin", "role": "admin", "name": "Admin"},
            "bs1": {"password": "123", "role": "doctor", "name": "BS. Nguyễn Văn A"},
            "bn1": {"password": "123", "role": "patient", "name": "Nguyễn Thị B", "info": {}},
            "bn2": {"password": "123", "role": "patient", "name": "Trần Văn C", "info": {}}
        }

        self.current_user = None
        self.current_role = None
        self.invoices = []  # Lưu trữ hóa đơn
        
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
        elif self.current_role == "doctor":
            self.create_doctor_menu(menu_frame)
        elif self.current_role == "receptionist":
            self.create_receptionist_menu(menu_frame)
        elif self.current_role == "patient":
            self.create_patient_menu(menu_frame)
    
    def create_admin_menu(self, parent):
        ttk.Button(parent, text="Quản lý bệnh nhân", command=self.show_patient_management).pack(fill="x", pady=2)
        ttk.Button(parent, text="Tạo hóa đơn", command=self.show_create_invoice).pack(fill="x", pady=2)
    
    def show_create_invoice(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="TẠO HÓA ĐƠN", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, pady=10, sticky="e")
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(frame, textvariable=patient_var, width=23)
        patient_combo['values'] = [self.users[u]["name"] for u in self.users if self.users[u]["role"] == "patient"]
        patient_combo.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Dịch vụ (Khám bệnh, xét nghiệm...):").grid(row=1, column=0, pady=10, sticky="e")
        service_entry = ttk.Entry(frame, width=25)
        service_entry.insert(0, "Khám bệnh")
        service_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Số tiền:").grid(row=2, column=0, pady=10, sticky="e")
        amount_entry = ttk.Entry(frame, width=25)
        amount_entry.grid(row=2, column=1, pady=10)
        
        ttk.Label(frame, text="Phương thức thanh toán:").grid(row=3, column=0, pady=10, sticky="e")
        payment_method = ttk.Combobox(frame, width=23)
        payment_method['values'] = ["Tiền mặt", "Thẻ tín dụng", "Chuyển khoản"]
        payment_method.grid(row=3, column=1, pady=10)
        
        def create_invoice():
            patient_name = patient_combo.get()
            service = service_entry.get()
            amount = amount_entry.get()
            payment = payment_method.get()
            
            if not patient_name or not service or not amount or not payment:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return
            
            # Tạo hóa đơn mới
            invoice = {
                "patient_name": patient_name,
                "service": service,
                "amount": amount,
                "payment_method": payment,
                "date": str(datetime.now())
            }
            
            # Lưu hóa đơn vào danh sách
            self.invoices.append(invoice)
            
            messagebox.showinfo("Thành công", "Đã tạo hóa đơn thành công!")
            self.show_invoice_list()  # Hiển thị danh sách hóa đơn
    
        ttk.Button(frame, text="Tạo hóa đơn", command=create_invoice).grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Quay lại", command=self.create_main_screen).grid(row=5, column=0, columnspan=2)
    
    def show_invoice_list(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="DANH SÁCH HÓA ĐƠN", font=("Arial", 16, "bold")).pack(pady=20)
        
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        # Treeview to show invoice details
        tree = ttk.Treeview(tree_frame, columns=("patient_name", "service", "amount", "payment_method", "date"), show="headings")
        tree.heading("patient_name", text="Tên bệnh nhân")
        tree.heading("service", text="Dịch vụ")
        tree.heading("amount", text="Số tiền")
        tree.heading("payment_method", text="Phương thức thanh toán")
        tree.heading("date", text="Ngày tạo hóa đơn")
        
        # Fill treeview with invoice data
        for invoice in self.invoices:
            tree.insert("", "end", values=(invoice["patient_name"], invoice["service"], invoice["amount"], invoice["payment_method"], invoice["date"]))
        
        tree.pack(fill="both", expand=True)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicManagementSystem(root)
    root.mainloop()

