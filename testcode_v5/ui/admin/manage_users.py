import tkinter as tk
from tkinter import ttk, messagebox
import json

class ManageUsersView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # === TOP SECTION ===
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(top_frame, text="QUẢN LÝ TÀI KHOẢN", font=("Arial", 16, "bold")).pack(side="left")
        
        # Search bar
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_users())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        # === TREEVIEW ===
        self.tree = ttk.Treeview(self, columns=("username", "name", "role"), show="headings", height=15)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("role", text="Vai trò")
        
        self.tree.column("username", width=150)
        self.tree.column("name", width=200)
        self.tree.column("role", width=100)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
        
        # === BUTTON FRAME ===
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Xem chi tiết", command=self.view_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Đổi mật khẩu", command=self.change_password).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Tạo tài khoản", command=self.create_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa tài khoản", command=self.delete_user).pack(side="left", padx=5)
        self.all_users = {}
        self.refresh_list()
    
    def refresh_list(self):
        """Làm mới danh sách tài khoản"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.all_users = self.controller.db.get_all_users()
        self.filter_users()
    
    def filter_users(self):
        """Lọc tài khoản theo tìm kiếm"""
        search_term = self.search_var.get().lower()
        role_map = {"admin": "Admin", "doctor": "Bác sĩ", "patient": "Bệnh nhân"}
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for username, info in self.all_users.items():
            if search_term in username.lower() or search_term in info["name"].lower():
                role_display = role_map.get(info["role"], info["role"])
                self.tree.insert("", "end", values=(username, info["name"], role_display))
    
    def get_selected_user(self):
        """Lấy tài khoản được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một tài khoản")
            return None
        return selection[0]
    
    def view_details(self):
        """Xem chi tiết tài khoản"""
        item_id = self.get_selected_user()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        user_data = self.controller.db.get_user(username)
        if not user_data:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return
        
        role_map = {"admin": "Admin", "doctor": "Bác sĩ", "patient": "Bệnh nhân",}
        role_display = role_map.get(user_data["role"], user_data["role"])
        
        details = f"""
Chi tiết tài khoản:
========================================
Tên đăng nhập: {username}
Họ tên: {user_data['name']}
Vai trò: {role_display}
Thông tin bổ sung: {user_data.get('info', 'N/A')}
        """
        
        messagebox.showinfo("Chi tiết tài khoản", details)
    
    def change_password(self):
        """Đổi mật khẩu tài khoản"""
        item_id = self.get_selected_user()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        if username == self.controller.auth.current_user and username != "admin":
            messagebox.showinfo("Thông báo", "Dùng tính năng đổi mật khẩu cá nhân để thay đổi mật khẩu của bạn")
            return
        
        change_win = tk.Toplevel(self)
        change_win.title(f"Đổi mật khẩu - {username}")
        change_win.geometry("350x180")
        
        ttk.Label(change_win, text=f"Đặt mật khẩu mới cho: {username}", font=("Arial", 11, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(change_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="Mật khẩu mới:").grid(row=0, column=0, sticky="e", padx=5, pady=10)
        new_pwd_entry = ttk.Entry(form_frame, width=30, show="*")
        new_pwd_entry.grid(row=0, column=1, padx=5, pady=10)
        
        ttk.Label(form_frame, text="Xác nhận mật khẩu:").grid(row=1, column=0, sticky="e", padx=5, pady=10)
        confirm_pwd_entry = ttk.Entry(form_frame, width=30, show="*")
        confirm_pwd_entry.grid(row=1, column=1, padx=5, pady=10)
        
        def save_password():
            new_pwd = new_pwd_entry.get()
            confirm_pwd = confirm_pwd_entry.get()
            
            if not new_pwd or not confirm_pwd:
                messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin")
                return
            
            if new_pwd != confirm_pwd:
                messagebox.showerror("Lỗi", "Mật khẩu không khớp")
                return
            
            try:
                from core.password_hasher import PasswordHasher
                hashed_pwd = PasswordHasher.hash_password(new_pwd)
                
                self.controller.db.cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed_pwd, username)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
                change_win.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Đổi mật khẩu thất bại: {str(e)}")
        
        ttk.Button(form_frame, text="Lưu", command=save_password).grid(row=2, column=0, columnspan=2, pady=20)
    
    def create_user(self):
        """Tạo tài khoản mới"""
        create_win = tk.Toplevel(self)
        create_win.title("Tạo tài khoản mới")
        create_win.geometry("380x300")
        
        ttk.Label(create_win, text="Tạo tài khoản mới", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(create_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="Tên đăng nhập:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        username_entry = ttk.Entry(form_frame, width=25)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Mật khẩu:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_entry = ttk.Entry(form_frame, width=25, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Họ tên:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        name_entry = ttk.Entry(form_frame, width=25)
        name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Vai trò:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        role_var = tk.StringVar(value="patient")
        role_combo = ttk.Combobox(form_frame, textvariable=role_var,
                                  values=["patient", "doctor", "admin"],
                                  state="readonly", width=22)
        role_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Chi nhánh/Chuyên khoa (tùy vai trò):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        extra_entry = ttk.Entry(form_frame, width=25)
        extra_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def create():
            try:
                from core.password_hasher import PasswordHasher
                
                username = username_entry.get().strip()
                password = password_entry.get()
                name = name_entry.get().strip()
                role = role_var.get()
                extra_info = extra_entry.get().strip()
                
                if not all([username, password, name]):
                    messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin bắt buộc")
                    return
                
                # Kiểm tra username tồn tại
                if self.controller.db.get_user(username):
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
                    return
                
                # Tạo info JSON dựa vào role
                if role == "doctor":
                    info_dict = {"branch": extra_info, "specialty": "", "exp": "", "rating": "", "price": ""}
                else:
                    info_dict = {}
                
                info_json = json.dumps(info_dict, ensure_ascii=False)
                
                self.controller.db.cursor.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                    (username, PasswordHasher.hash_password(password), role, name, info_json)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", f"Tạo tài khoản {username} thành công!")
                create_win.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Tạo thất bại: {str(e)}")
        
        ttk.Button(form_frame, text="Tạo", command=create).grid(row=5, column=0, columnspan=2, pady=20)
    
    def delete_user(self):
        """Xóa tài khoản"""
        item_id = self.get_selected_user()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        name = values[1]
        
        if username == "admin":
            messagebox.showerror("Lỗi", "Không thể xóa tài khoản admin")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa tài khoản {username} ({name})?"):
            try:
                self.controller.db.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xóa tài khoản thành công!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")