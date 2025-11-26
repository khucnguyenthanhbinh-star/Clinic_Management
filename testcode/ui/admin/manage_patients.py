import tkinter as tk
from tkinter import ttk, messagebox
import json

class ManagePatientsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ BỆNH NHÂN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_patients())
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Xem chi tiết", command=self.view_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xem lịch hẹn", command=self.view_appointments).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_patient).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("username", "name", "phone", "appointments"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("name", text="Họ tên")
        self.tree.heading("phone", text="Điện thoại")
        self.tree.heading("appointments", text="Số lịch hẹn")
        
        self.tree.column("username", width=120)
        self.tree.column("name", width=150)
        self.tree.column("phone", width=120)
        self.tree.column("appointments", width=100)
        self.tree.pack(fill="both", expand=True)
        
        self.patients = {}
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        patients = self.controller.db.get_users_by_role("patient")
        appointments = self.controller.db.get_appointments()
        
        self.patients = {}
        for p in patients:
            count = len([a for a in appointments if a["patient"] == p["username"]])
            
            try:
                info = json.loads(p.get("info", "{}"))
                phone = info.get("phone", "---")
            except:
                phone = "---"
            
            self.patients[p["username"]] = {"name": p["name"], "phone": phone, "appointments": count}
            self.tree.insert("", "end", values=(p["username"], p["name"], phone, count))

    def filter_patients(self):
        search_text = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())
        
        for username, info in self.patients.items():
            if search_text in username.lower() or search_text in info["name"].lower():
                self.tree.insert("", "end", values=(username, info["name"], info["phone"], info["appointments"]))

    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        patient = self.controller.db.get_user(username)
        if not patient:
            messagebox.showerror("Lỗi", "Không tìm thấy bệnh nhân")
            return
        
        try:
            info = json.loads(patient.get("info", "{}"))
        except:
            info = {}
        
        details = f"""
        Thông tin bệnh nhân:
        
        Tên đăng nhập: {username}
        Họ tên: {patient['name']}
        Số điện thoại: {info.get('phone', '---')}
        Địa chỉ: {info.get('address', '---')}
        Ngày sinh: {info.get('dob', '---')}
        Giới tính: {info.get('gender', '---')}
        CCCD: {info.get('cccd', '---')}
        Bảo hiểm: {info.get('insurance', '---')}
        Nhóm máu: {info.get('blood_type', '---')}
        Cân nặng: {info.get('weight', '---')} kg
        Chiều cao: {info.get('height', '---')} cm
        Tiền sử: {info.get('history', 'Không')}
        """
        
        messagebox.showinfo("Chi tiết bệnh nhân", details)

    def view_appointments(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        appointments = self.controller.db.get_appointments(username)
        
        if not appointments:
            messagebox.showinfo("Lịch hẹn", "Bệnh nhân này chưa có lịch hẹn nào")
            return
        
        msg = f"Lịch hẹn của {username}:\n\n"
        for apt in appointments:
            msg += f"ID: {apt['id']} | Ngày: {apt['date']} | Giờ: {apt['time']} | Trạng thái: {apt['status']}\n"
        
        messagebox.showinfo("Lịch hẹn", msg)

    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân")
            return
        
        item = self.tree.item(selected[0])
        username = item["values"][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {username}? Tất cả lịch hẹn và hóa đơn sẽ bị xóa."):
            success, msg = self.controller.db.delete_user(username)
            if success:
                messagebox.showinfo("Thành công", "Xóa bệnh nhân thành công")
                self.refresh_tree()
            else:
                messagebox.showerror("Lỗi", msg)
