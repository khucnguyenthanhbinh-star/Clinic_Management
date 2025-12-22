import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json

class ManagePatientsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.patients = []
        self.appointments = []
        
        # === TOP SECTION: TITLE + SEARCH ===
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(top_frame, text="QUẢN LÝ BỆNH NHÂN", font=("Arial", 16, "bold")).pack(side="left")
        
        # Search bar
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side="right", padx=5)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_patients())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        # === TREEVIEW ===
        self.tree = ttk.Treeview(self, columns=("username", "name", "phone", "appointments"), show="headings", height=15)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("phone", text="Điện thoại")
        self.tree.heading("appointments", text="Số lịch hẹn")
        
        self.tree.column("username", width=120)
        self.tree.column("name", width=150)
        self.tree.column("phone", width=120)
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
        ttk.Button(btn_frame, text="Cập nhật thông tin", command=self.edit_patient).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa bệnh nhân", command=self.delete_patient).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Tạo", command=self.create_patient).pack(side="left", padx=5)
        self.refresh_list()
        
    def refresh_list(self):
        """Làm mới danh sách bệnh nhân"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.patients = self.controller.db.get_users_by_role("patient")
        self.appointments = self.controller.db.get_appointments()
        self.filter_patients()
    
    def filter_patients(self):
        """Lọc bệnh nhân theo tìm kiếm"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for p in self.patients:
            if search_term in p["username"].lower() or search_term in p["name"].lower():
                count = len([a for a in self.appointments if a["patient"] == p["username"]])
                
                # Lấy số điện thoại từ info JSON
                phone = ""
                try:
                    info = json.loads(p.get("info", "{}"))
                    phone = info.get("phone", "")
                except:
                    pass
                
                self.tree.insert("", "end", values=(p["username"], p["name"], phone, count))
    
    def get_selected_patient(self):
        """Lấy bệnh nhân được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một bệnh nhân")
            return None
        return selection[0]
    
    def view_details(self):
        """Xem chi tiết bệnh nhân"""
        item_id = self.get_selected_patient()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        user_data = self.controller.db.get_user(username)
        if not user_data:
            messagebox.showerror("Lỗi", "Không tìm thấy bệnh nhân")
            return
        
        try:
            info = json.loads(user_data["info"])
        except:
            info = {}
        
        details = f"""
Thông tin bệnh nhân:
========================================
Tên đăng nhập: {username}
Họ tên: {user_data['name']}
Ngày sinh: {info.get('dob', 'N/A')}
Giới tính: {info.get('gender', 'N/A')}
Số điện thoại: {info.get('phone', 'N/A')}
CCCD: {info.get('cccd', 'N/A')}
Địa chỉ: {info.get('address', 'N/A')}
Lịch sử bệnh: {info.get('history', 'N/A')}
Bảo hiểm: {info.get('insurance', 'N/A')}
        """
        
        messagebox.showinfo("Chi tiết bệnh nhân", details)
    
    def edit_patient(self):
        """Cập nhật thông tin bệnh nhân"""
        item_id = self.get_selected_patient()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        
        user_data = self.controller.db.get_user(username)
        if not user_data:
            messagebox.showerror("Lỗi", "Không tìm thấy bệnh nhân")
            return
        
        try:
            info = json.loads(user_data["info"])
        except:
            info = {}
        
        # Tạo cửa sổ edit
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Cập nhật - {username}")
        edit_win.geometry("400x350")
        
        tk.Label(edit_win, text="Cập nhật thông tin bệnh nhân", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(edit_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields = [
            ("Họ tên:", "name", user_data.get("name", "")),
            ("Ngày sinh:", "dob", info.get("dob", "")),
            ("Giới tính:", "gender", info.get("gender", "")),
            ("Số điện thoại:", "phone", info.get("phone", "")),
            ("CCCD:", "cccd", info.get("cccd", "")),
            ("Địa chỉ:", "address", info.get("address", "")),
            ("Lịch sử bệnh:", "history", info.get("history", "")),
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
                # Cập nhật tên
                new_name = entries["name"].get()
                new_info = {
                    "dob": entries["dob"].get(),
                    "gender": entries["gender"].get(),
                    "phone": entries["phone"].get(),
                    "cccd": entries["cccd"].get(),
                    "address": entries["address"].get(),
                    "history": entries["history"].get(),
                    "insurance": info.get("insurance", "")
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
    
    def delete_patient(self):
        """Xóa bệnh nhân"""
        item_id = self.get_selected_patient()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        username = values[0]
        name = values[1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa bệnh nhân {name}?"):
            try:
                self.controller.db.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xóa bệnh nhân thành công!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")
    
    def create_patient(self):
        """Tạo bệnh nhân mới"""
        create_win = tk.Toplevel(self)
        create_win.title("Tạo bệnh nhân mới")
        create_win.geometry("400x300")
        
        tk.Label(create_win, text="Tạo bệnh nhân mới", font=("Arial", 12, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(create_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(form_frame, text="Tên đăng nhập:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Mật khẩu:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_entry = ttk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Họ tên:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Số điện thoại:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        phone_entry = ttk.Entry(form_frame, width=30)
        phone_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Địa chỉ:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def create():
            username = username_entry.get()
            password = password_entry.get()
            name = name_entry.get()
            phone = phone_entry.get()
            address = address_entry.get()
            
            if not all([username, password, name]):
                messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin")
                return
            
            try:
                from core.password_hasher import PasswordHasher
                info_dict = {"phone": phone, "address": address, "dob": "", "gender": "", "cccd": "", "history": "", "insurance": ""}
                info_json = json.dumps(info_dict, ensure_ascii=False)
                
                self.controller.db.cursor.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                    (username, PasswordHasher.hash_password(password), "patient", name, info_json)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Tạo bệnh nhân thành công!")
                create_win.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Tạo thất bại: {str(e)}")
        
        ttk.Button(form_frame, text="Tạo", command=create).grid(row=5, column=0, columnspan=2, pady=20)