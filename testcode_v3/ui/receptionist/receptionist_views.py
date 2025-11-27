import tkinter as tk
from tkinter import ttk, messagebox

class CreateInvoiceView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="TẠO HÓA ĐƠN", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, pady=10, sticky="e")
        patient_combo = ttk.Combobox(frame, values=[self.controller.db.users[u]["name"] for u in self.controller.db.users if self.controller.db.users[u]["role"] == "patient"])
        patient_combo.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Dịch vụ:").grid(row=1, column=0, pady=10, sticky="e")
        service_entry = ttk.Entry(frame)
        service_entry.insert(0, "Khám bệnh")
        service_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Số tiền:").grid(row=2, column=0, pady=10, sticky="e")
        amount_entry = ttk.Entry(frame)
        amount_entry.insert(0, "200000")
        amount_entry.grid(row=2, column=1, pady=10)
        
        ttk.Button(frame, text="Tạo hóa đơn", command=lambda: messagebox.showinfo("Thành công", "Đã tạo hóa đơn!")).grid(row=3, column=0, columnspan=2, pady=20)

class SendNotificationView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="GỬI THÔNG BÁO", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Gửi đến:").grid(row=0, column=0, pady=10, sticky="e")
        values = ["Tất cả bệnh nhân"] + [self.controller.db.users[u]["name"] for u in self.controller.db.users if self.controller.db.users[u]["role"] == "patient"]
        ttk.Combobox(frame, values=values).grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Tiêu đề:").grid(row=1, column=0, pady=10, sticky="e")
        ttk.Entry(frame).grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Nội dung:").grid(row=2, column=0, pady=10, sticky="ne")
        tk.Text(frame, width=30, height=5).grid(row=2, column=1, pady=10)
        
        ttk.Button(frame, text="Gửi thông báo", command=lambda: messagebox.showinfo("Thành công", "Đã gửi thông báo!")).grid(row=3, column=0, columnspan=2, pady=20)