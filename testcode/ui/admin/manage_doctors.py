import tkinter as tk
from tkinter import ttk

class ManageDoctorsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ BÁC SĨ", font=("Arial", 16, "bold")).pack(pady=20)
        tree = ttk.Treeview(self, columns=("username", "name"), show="headings")
        tree.heading("username", text="Tên đăng nhập")
        tree.heading("name", text="Họ tên")
        
        # Lấy list bác sĩ từ DB
        doctors = self.controller.db.get_users_by_role("doctor")
        
        for doc in doctors:
            tree.insert("", "end", values=(doc["username"], doc["name"]))
            
        tree.pack(fill="both", expand=True, padx=20)