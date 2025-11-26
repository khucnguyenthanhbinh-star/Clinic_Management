import tkinter as tk
from tkinter import ttk

class ManageUsersView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ TÀI KHOẢN", font=("Arial", 16, "bold")).pack(pady=20)
        tree = ttk.Treeview(self, columns=("username", "name", "role"), show="headings")
        tree.heading("username", text="Tên đăng nhập")
        tree.heading("name", text="Họ tên")
        tree.heading("role", text="Vai trò")
        
        role_map = {"admin": "Admin", "doctor": "Bác sĩ", "patient": "Bệnh nhân", "receptionist": "Lễ tân"}
        
        users = self.controller.db.get_all_users()
        # users trả về dict: {username: {'name':..., 'role':...}}
        
        for username, info in users.items():
            role_display = role_map.get(info["role"], info["role"])
            tree.insert("", "end", values=(username, info["name"], role_display))
            
        tree.pack(fill="both", expand=True, padx=20)