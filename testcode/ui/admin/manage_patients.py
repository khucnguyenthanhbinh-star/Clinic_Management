import tkinter as tk
from tkinter import ttk

class ManagePatientsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ BỆNH NHÂN", font=("Arial", 16, "bold")).pack(pady=20)
        tree = ttk.Treeview(self, columns=("username", "name", "appointments"), show="headings")
        tree.heading("username", text="Tên đăng nhập")
        tree.heading("name", text="Họ tên")
        tree.heading("appointments", text="Số lịch hẹn")
        
        patients = self.controller.db.get_users_by_role("patient")
        appointments = self.controller.db.get_appointments()
        
        for p in patients:
            # Đếm số lịch hẹn của bệnh nhân này
            count = len([a for a in appointments if a["patient"] == p["username"]])
            tree.insert("", "end", values=(p["username"], p["name"], count))
            
        tree.pack(fill="both", expand=True, padx=20)