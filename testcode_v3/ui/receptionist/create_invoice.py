import tkinter as tk
from tkinter import ttk, messagebox

class CreateInvoiceView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="TẠO HÓA ĐƠN", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        # Lấy danh sách bệnh nhân từ DB để hiển thị trong Combobox
        # Lưu ý: Hàm get_users_by_role trả về list dict
        patients = self.controller.db.get_users_by_role("patient")
        patient_names = [p["name"] for p in patients]
        
        ttk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, pady=10, sticky="e")
        self.patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(frame, textvariable=self.patient_var, width=23, values=patient_names)
        patient_combo.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Dịch vụ:").grid(row=1, column=0, pady=10, sticky="e")
        self.service_entry = ttk.Entry(frame, width=25)
        self.service_entry.insert(0, "Khám bệnh")
        self.service_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Số tiền (VNĐ):").grid(row=2, column=0, pady=10, sticky="e")
        self.amount_entry = ttk.Entry(frame, width=25)
        self.amount_entry.insert(0, "200000")
        self.amount_entry.grid(row=2, column=1, pady=10)
        
        ttk.Button(frame, text="Tạo hóa đơn", command=self.create_invoice).grid(row=3, column=0, columnspan=2, pady=20)

    def create_invoice(self):
        patient = self.patient_var.get()
        amount = self.amount_entry.get()
        if patient and amount:
            messagebox.showinfo("Thành công", f"Đã xuất hóa đơn {amount} VNĐ cho bệnh nhân {patient}!")
        else:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")