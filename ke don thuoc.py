import tkinter as tk
from tkinter import ttk, messagebox

class ClinicManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Phòng khám")
        self.root.geometry("1200x700")
        
        # Dữ liệu mẫu thuốc (có thể thay đổi)
        self.medicines = {
            "Paracetamol": {"quantity": 100, "unit": "viên"},
            "Amoxicillin": {"quantity": 50, "unit": "viên"},
            "Vitamin C": {"quantity": 80, "unit": "viên"}
        }
        
        self.current_user = "bs1"  # Giả sử bác sĩ đang đăng nhập
        self.users = {
            "bs1": {"password": "123", "role": "doctor", "name": "BS. Nguyễn Văn A"},
            "bn1": {"password": "123", "role": "patient", "name": "Nguyễn Thị B"}
        }
        
        self.appointments = [
            {"patient": "bn1", "date": "2025-11-20", "time": "09:00", "reason": "Đau bụng", "status": "Đã đặt"}
        ]
        
        self.create_main_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_main_screen(self):
        self.clear_screen()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Xin chào: {self.users[self.current_user]['name']}", 
                 font=("Arial", 12)).pack(side="left")
        ttk.Button(top_frame, text="Đăng xuất", command=self.clear_screen).pack(side="right")
        
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
        self.create_doctor_menu(menu_frame)
    
    def create_doctor_menu(self, parent):
        ttk.Button(parent, text="Kê đơn thuốc", command=self.show_prescription).pack(fill="x", pady=2)
        ttk.Button(parent, text="Danh sách khám", command=self.show_examination_list).pack(fill="x", pady=2)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_prescription(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="KÊ ĐƠN THUỐC", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        # Chọn thuốc
        ttk.Label(frame, text="Chọn thuốc:").grid(row=0, column=0, pady=10, sticky="e")
        medicine_var = tk.StringVar()
        medicine_combo = ttk.Combobox(frame, textvariable=medicine_var, width=23)
        medicine_combo['values'] = list(self.medicines.keys())  # Hiển thị danh sách thuốc
        medicine_combo.grid(row=0, column=1, pady=10)
        
        # Số lượng
        ttk.Label(frame, text="Số lượng:").grid(row=1, column=0, pady=10, sticky="e")
        quantity_entry = ttk.Entry(frame, width=25)
        quantity_entry.grid(row=1, column=1, pady=10)
        
        # Hướng dẫn sử dụng
        ttk.Label(frame, text="Hướng dẫn sử dụng:").grid(row=2, column=0, pady=10, sticky="ne")
        instruction_text = tk.Text(frame, width=30, height=3)
        instruction_text.grid(row=2, column=1, pady=10)
        
        # Danh sách thuốc đã kê
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("medicine", "quantity", "instruction"), show="headings")
        tree.heading("medicine", text="Thuốc")
        tree.heading("quantity", text="Số lượng")
        tree.heading("instruction", text="Hướng dẫn")
        tree.pack(fill="both", expand=True)
        
        # Hàm thêm thuốc vào danh sách kê đơn
        def add_medicine():
            medicine = medicine_var.get()
            quantity = quantity_entry.get()
            instruction = instruction_text.get("1.0", "end-1c")  # Lấy dữ liệu từ Textbox
            
            if medicine and quantity:
                tree.insert("", "end", values=(medicine, quantity, instruction))
                medicine_combo.set("")  # Xóa mục đã chọn sau khi thêm
                quantity_entry.delete(0, "end")  # Xóa ô nhập số lượng
                instruction_text.delete("1.0", "end")  # Xóa phần hướng dẫn
    
        # Thêm thuốc vào kê đơn
        ttk.Button(frame, text="Thêm thuốc", command=add_medicine).grid(row=3, column=0, columnspan=2, pady=10)
    
        # Lưu kê đơn (bác sĩ hoàn thành đơn)
        def save_prescription():
            messagebox.showinfo("Thành công", "Đã lưu kê đơn thuốc!")
            self.show_examination_list()  # Quay lại danh sách khám sau khi lưu kê đơn
    
        # Lưu kê đơn
        ttk.Button(frame, text="Lưu kê đơn", command=save_prescription).grid(row=4, column=0, columnspan=2, pady=20)
    
    def show_examination_list(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="DANH SÁCH KHÁM", font=("Arial", 16, "bold")).pack(pady=20)
        
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        tree = ttk.Treeview(tree_frame, columns=("patient", "date", "time", "reason"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("reason", text="Lý do")
        
        for apt in self.appointments:
            patient_name = self.users.get(apt["patient"], {}).get("name", apt["patient"])
            tree.insert("", "end", values=(patient_name, apt["date"], apt["time"], apt["reason"]))
        
        tree.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicManagementSystem(root)
    root.mainloop()
