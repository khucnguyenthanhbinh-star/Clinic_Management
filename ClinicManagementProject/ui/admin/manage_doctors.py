import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json

class ManageDoctorsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.doctors = []
        self.appointments = []
        
        # === TOP SECTION: TITLE + SEARCH ===
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(top_frame, text="QUẢN LÝ BÁC SĨ", font=("Arial", 16, "bold")).pack(side="left")
        
        # Search bar
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side="right", padx=5)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_doctors())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        # === TREEVIEW ===
        self.tree = ttk.Treeview(self, columns=("username", "name", "specialty", "branch", "appointments"), show="headings", height=15)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("specialty", text="Chuyên khoa")
        self.tree.heading("branch", text="Chi nhánh")
        self.tree.heading("appointments", text="Số lịch hẹn")
        
        self.tree.column("username", width=110)
        self.tree.column("name", width=140)
        self.tree.column("specialty", width=120)
        self.tree.column("branch", width=80)
        self.tree.column("appointments", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
        
        # === BUTTON FRAME ===
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Xem chi tiết", command=self.view_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cập nhật thông tin", command=self.edit_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa bác sĩ", command=self.delete_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Tạo mới", command=self.create_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.refresh_list).pack(side="left", padx=5)
        
        self.refresh_list()
        
    def refresh_list(self):
        """Làm mới danh sách bác sĩ"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.doctors = self.controller.db.get_users_by_role("doctor")
        self.appointments = self.controller.db.get_appointments()
        self.filter_doctors()
    
    def filter_doctors(self):
        """Lọc bác sĩ theo tìm kiếm"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for doc in self.doctors:
            if search_term in doc["username"].lower() or search_term in doc["name"].lower():
                try:
                    info = json.loads(doc.get("info", "{}"))
                    specialty = info.get("specialty", "N/A")
                    branch = info.get("branch", "N/A")
                except:
                    specialty = "N/A"
                    branch = "N/A"
                
                count = len([a for a in self.appointments if "[BS" in a.get("reason", "") and doc["username"] in a.get("reason", "")])
                
                self.tree.insert("", "end", values=(doc["username"], doc["name"], specialty, branch, count))
    
    def get_selected_doctor(self):
        """Lấy bác sĩ được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một bác sĩ")
            return None
        return selection[0]
    
    def view_details(self):
        """Xem chi tiết bác sĩ"""
        item_id = self.get_selected_doctor()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        user_data = self.controller.db.get_user(username)
        if not user_data:
            messagebox.showerror("Lỗi", "Không tìm thấy bác sĩ")
            return
        
        try:
            info = json.loads(user_data["info"])
        except:
            info = {}
        
        details = f"""
Thông tin bác sĩ:
========================================
Tên đăng nhập: {username}
Họ tên: {user_data['name']}
Chuyên khoa: {info.get('specialty', 'N/A')}
Chi nhánh: {info.get('branch', 'N/A')}
Kinh nghiệm: {info.get('exp', 'N/A')} năm
Đánh giá: {info.get('rating', 'N/A')} ⭐
Giá khám: {info.get('price', 'N/A')} đ
Số điện thoại: {info.get('phone', 'N/A')}
Hình ảnh: {info.get('image', 'N/A')}
        """
        
        messagebox.showinfo("Chi tiết bác sĩ", details)
    
    def edit_doctor(self):
        """Cập nhật thông tin bác sĩ"""
        item_id = self.get_selected_doctor()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        user_data = self.controller.db.get_user(username)
        if not user_data:
            messagebox.showerror("Lỗi", "Không tìm thấy bác sĩ")
            return
        
        try:
            info = json.loads(user_data["info"])
        except:
            info = {}
        
        # Tạo cửa sổ edit
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Cập nhật - {username}")
        edit_win.geometry("400x400")
        
        tk.Label(edit_win, text="Cập nhật thông tin bác sĩ", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(edit_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("Họ tên:", "name", user_data.get("name", "")),
            ("Chuyên khoa:", "specialty", info.get("specialty", "")),
            ("Chi nhánh:", "branch", info.get("branch", "")),
            ("Kinh nghiệm (năm):", "exp", info.get("exp", "")),
            ("Đánh giá (sao):", "rating", info.get("rating", "")),
            ("Giá khám (đ):", "price", info.get("price", "")),
            ("Số điện thoại:", "phone", info.get("phone", "")),
            ("Hình ảnh:", "image", info.get("image", "")),
        ]
        
        entries = {}
        for i, (label, key, value) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        def save_changes():
            try:
                new_name = entries["name"].get()
                new_info = {
                    "specialty": entries["specialty"].get(),
                    "branch": entries["branch"].get(),
                    "exp": entries["exp"].get(),
                    "rating": entries["rating"].get(),
                    "price": entries["price"].get(),
                    "phone": entries["phone"].get(),
                    "image": entries["image"].get(),
                }
                
                self.controller.db.cursor.execute(
                    "UPDATE users SET name = ?, info = ? WHERE username = ?",
                    (new_name, json.dumps(new_info, ensure_ascii=False), username)
                )
                self.controller.db.conn.commit()
                
                messagebox.showinfo("Thành công", "Cập nhật thông tin thành công!")
                edit_win.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Cập nhật thất bại: {str(e)}")
        
        ttk.Button(form_frame, text="Lưu", command=save_changes).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def delete_doctor(self):
        """Xóa bác sĩ"""
        item_id = self.get_selected_doctor()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        name = values[1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa bác sĩ {name}?"):
            try:
                self.controller.db.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xóa bác sĩ thành công!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")
    
    def create_doctor(self):
        """Tạo bác sĩ mới"""
        create_win = tk.Toplevel(self)
        create_win.title("Tạo bác sĩ mới")
        create_win.geometry("400x450")
        
        tk.Label(create_win, text="Tạo bác sĩ mới", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(create_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("Tên đăng nhập:", "username"),
            ("Mật khẩu:", "password"),
            ("Họ tên:", "name"),
            ("Chuyên khoa:", "specialty"),
            ("Chi nhánh:", "branch"),
            ("Kinh nghiệm (năm):", "exp"),
            ("Đánh giá:", "rating"),
            ("Giá khám:", "price"),
            ("Số điện thoại:", "phone"),
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            if key == "password":
                entry = ttk.Entry(form_frame, width=30, show="*")
            else:
                entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        def create():
            try:
                from core.password_hasher import PasswordHasher
                
                username = entries["username"].get()
                password = entries["password"].get()
                name = entries["name"].get()
                
                if not all([username, password, name]):
                    messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin bắt buộc")
                    return
                
                info_dict = {
                    "specialty": entries["specialty"].get(),
                    "branch": entries["branch"].get(),
                    "exp": entries["exp"].get(),
                    "rating": entries["rating"].get(),
                    "price": entries["price"].get(),
                    "phone": entries["phone"].get(),
                    "image": "doc_male.png"
                }
                info_json = json.dumps(info_dict, ensure_ascii=False)
                
                self.controller.db.cursor.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                    (username, PasswordHasher.hash_password(password), "doctor", name, info_json)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Tạo bác sĩ thành công!")
                create_win.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Tạo thất bại: {str(e)}")
        
        ttk.Button(form_frame, text="Tạo", command=create).grid(row=len(fields), column=0, columnspan=2, pady=20)