import tkinter as tk
from tkinter import ttk, messagebox

class SendNotificationView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="GỬI THÔNG BÁO", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Gửi đến:").grid(row=0, column=0, pady=10, sticky="e")
        
        # Lấy danh sách bệnh nhân
        patients = self.controller.db.get_users_by_role("patient")
        values = ["Tất cả bệnh nhân"] + [p["name"] for p in patients]
        
        self.recipient_combo = ttk.Combobox(frame, width=23, values=values)
        self.recipient_combo.current(0)
        self.recipient_combo.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Tiêu đề:").grid(row=1, column=0, pady=10, sticky="e")
        self.title_entry = ttk.Entry(frame, width=25)
        self.title_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Nội dung:").grid(row=2, column=0, pady=10, sticky="ne")
        self.content_text = tk.Text(frame, width=30, height=5)
        self.content_text.grid(row=2, column=1, pady=10)
        
        ttk.Button(frame, text="Gửi thông báo", command=self.send).grid(row=3, column=0, columnspan=2, pady=20)

    def send(self):
        recipient = self.recipient_combo.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", "end-1c")
        
        if title and content:
            messagebox.showinfo("Thành công", f"Đã gửi thông báo tới: {recipient}")
            # Clear form
            self.title_entry.delete(0, "end")
            self.content_text.delete("1.0", "end")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập tiêu đề và nội dung")