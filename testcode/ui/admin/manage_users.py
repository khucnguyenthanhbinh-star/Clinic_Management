import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ManageUsersView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ TÀI KHOẢN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_users())
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Thêm người dùng", command=self.add_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sửa", command=self.edit_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_user).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("username", "name", "role"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("role", text="Vai trò")
        self.tree.column("username", width=120)
        self.tree.column("name", width=200)
        self.tree.column("role", width=100)
        self.tree.pack(fill="both", expand=True)
        
        self.role_map = {"admin": "Admin", "doctor": "Bác sĩ", "patient": "Bệnh nhân", "receptionist": "Lễ tân"}
        self.all_users = {}
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.all_users = self.controller.db.get_all_users()
        for username, info in self.all_users.items():
            role_display = self.role_map.get(info["role"], info["role"])
            self.tree.insert("", "end", values=(username, info["name"], role_display))

    def filter_users(self):
        search_text = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())
        for username, info in self.all_users.items():
            if search_text in username.lower() or search_text in info["name"].lower():
                role_display = self.role_map.get(info["role"], info["role"])
                self.tree.insert("", "end", values=(username, info["name"], role_display))

    def add_user(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm người dùng")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Tên đăng nhập:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        username_entry = ttk.Entry(dialog, width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Mật khẩu:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        password_entry = ttk.Entry(dialog, width=25, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Họ tên:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=25)
        name_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Vai trò:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        role_combo = ttk.Combobox(dialog, values=["admin", "doctor", "patient", "receptionist"], width=23, state="readonly")
        role_combo.grid(row=3, column=1, padx=10, pady=5)
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            name = name_entry.get().strip()
            role = role_combo.get()
            
            if not all([username, password, name, role]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
                return
            
            success, msg = self.controller.db.add_user(username, password, role, name)
            if success:
                messagebox.showinfo("Thành công", "Thêm người dùng thành công")
                self.refresh_tree()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg)
        
        ttk.Button(dialog, text="Lưu", command=save).grid(row=4, column=0, columnspan=2, pady=20)

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để sửa")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        user = self.controller.db.get_user(username)
        if not user:
            messagebox.showerror("Lỗi", "Không tìm thấy người dùng")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Sửa người dùng: {username}")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Họ tên:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=25)
        name_entry.insert(0, user["name"])
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Vai trò:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        role_combo = ttk.Combobox(dialog, values=["admin", "doctor", "patient", "receptionist"], width=23, state="readonly")
        role_combo.set(user["role"])
        role_combo.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Mật khẩu mới (để trống nếu không đổi):").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        password_entry = ttk.Entry(dialog, width=25, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save():
            name = name_entry.get().strip()
            role = role_combo.get()
            password = password_entry.get().strip() if password_entry.get() else None
            
            if not name or not role:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
                return
            
            success, msg = self.controller.db.update_user(username, name=name, role=role, password=password)
            if success:
                messagebox.showinfo("Thành công", "Cập nhật thành công")
                self.refresh_tree()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg)
        
        ttk.Button(dialog, text="Lưu", command=save).grid(row=3, column=0, columnspan=2, pady=20)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để xóa")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {username}?"):
            success, msg = self.controller.db.delete_user(username)
            if success:
                messagebox.showinfo("Thành công", "Xóa người dùng thành công")
                self.refresh_tree()
            else:
                messagebox.showerror("Lỗi", msg)
