import tkinter as tk
from tkinter import ttk, messagebox
import json

class ManageDoctorsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ BÁC SĨ", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Xem chi tiết", command=self.view_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sửa", command=self.edit_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_doctor).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("username", "name", "specialty"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("specialty", text="Chuyên khoa")
        
        self.tree.column("username", width=120)
        self.tree.column("name", width=200)
        self.tree.column("specialty", width=150)
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        doctors = self.controller.db.get_users_by_role("doctor")
        
        for doc in doctors:
            specialty = "---"
            try:
                info = json.loads(doc.get("info", "{}"))
                specialty = info.get("specialty", "---")
            except:
                pass
            
            self.tree.insert("", "end", values=(doc["username"], doc["name"], specialty))

    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bác sĩ")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        doctor = self.controller.db.get_user(username)
        if not doctor:
            messagebox.showerror("Lỗi", "Không tìm thấy bác sĩ")
            return
        
        try:
            info = json.loads(doctor.get("info", "{}"))
        except:
            info = {}
        
        # Count appointments
        appointments = self.controller.db.get_appointments()
        count = len([a for a in appointments if a.get("doctor") == username])
        
        details = f"""
        Thông tin bác sĩ:
        
        Tên đăng nhập: {username}
        Họ tên: {doctor['name']}
        Chuyên khoa: {info.get('specialty', 'Chưa cập nhật')}
        Kinh nghiệm: {info.get('exp', 'Chưa cập nhật')} năm
        Đánh giá: {info.get('rating', 'Chưa cập nhật')}/5.0
        Giá khám: {info.get('price', 'Chưa cập nhật')} VNĐ
        Chi nhánh: {info.get('branch', 'Chưa cập nhật')}
        Số điện thoại: {info.get('phone', 'Chưa cập nhật')}
        Số lịch hẹn: {count}
        """
        
        messagebox.showinfo("Chi tiết bác sĩ", details)

    def edit_doctor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bác sĩ")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        doctor = self.controller.db.get_user(username)
        if not doctor:
            messagebox.showerror("Lỗi", "Không tìm thấy bác sĩ")
            return
        
        try:
            info = json.loads(doctor.get("info", "{}"))
        except:
            info = {}
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Sửa bác sĩ: {username}")
        dialog.geometry("450x400")
        
        ttk.Label(dialog, text="Họ tên:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, doctor["name"])
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Chuyên khoa:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        specialty_entry = ttk.Entry(dialog, width=30)
        specialty_entry.insert(0, info.get("specialty", ""))
        specialty_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Kinh nghiệm (năm):").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        exp_entry = ttk.Entry(dialog, width=30)
        exp_entry.insert(0, str(info.get("exp", "")))
        exp_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Đánh giá (0-5):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        rating_entry = ttk.Entry(dialog, width=30)
        rating_entry.insert(0, str(info.get("rating", "")))
        rating_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Giá khám (VNĐ):").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        price_entry = ttk.Entry(dialog, width=30)
        price_entry.insert(0, str(info.get("price", "")))
        price_entry.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Chi nhánh:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        branch_entry = ttk.Entry(dialog, width=30)
        branch_entry.insert(0, info.get("branch", ""))
        branch_entry.grid(row=5, column=1, padx=10, pady=5)
        
        def save():
            name = name_entry.get().strip()
            specialty = specialty_entry.get().strip()
            exp = exp_entry.get().strip()
            rating = rating_entry.get().strip()
            price = price_entry.get().strip()
            branch = branch_entry.get().strip()
            
            if not name or not specialty:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
                return
            
            try:
                new_info = {
                    "specialty": specialty,
                    "exp": int(exp) if exp else 0,
                    "rating": float(rating) if rating else 0,
                    "price": int(price) if price else 0,
                    "branch": branch,
                    "phone": info.get("phone", ""),
                    "image": info.get("image", "doc_male.png")
                }
            except:
                messagebox.showerror("Lỗi", "Kinh nghiệm/Đánh giá/Giá phải là số")
                return
            
            success, msg = self.controller.db.update_user(username, name=name, info=json.dumps(new_info, ensure_ascii=False))
            if success:
                messagebox.showinfo("Thành công", "Cập nhật thành công")
                self.refresh_tree()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg)
        
        ttk.Button(dialog, text="Lưu", command=save).grid(row=6, column=0, columnspan=2, pady=20)

    def delete_doctor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bác sĩ")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {username}? Tất cả lịch hẹn sẽ bị xóa."):
            success, msg = self.controller.db.delete_user(username)
            if success:
                messagebox.showinfo("Thành công", "Xóa bác sĩ thành công")
                self.refresh_tree()
            else:
                messagebox.showerror("Lỗi", msg)
