import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ManageAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # === TOP SECTION ===
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(top_frame, text="QUẢN LÝ LỊCH HẸN", font=("Arial", 16, "bold")).pack(side="left")
        
        # Filter by status
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(side="right")
        ttk.Label(filter_frame, text="Trạng thái:").pack(side="left", padx=5)
        self.status_var = tk.StringVar(value="Tất cả")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                    values=["Tất cả", "Đã đặt", "Checked-in", "Hoan thanh", "Đã hủy"],
                                    state="readonly", width=15)
        status_combo.pack(side="left", padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())
        
        # === TREEVIEW ===
        self.tree = ttk.Treeview(self, columns=("id", "patient", "date", "time", "reason", "status"), show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("patient", text="Bệnh nhân")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("reason", text="Lý do/Ghi chú")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=40)
        self.tree.column("patient", width=120)
        self.tree.column("date", width=100)
        self.tree.column("time", width=70)
        self.tree.column("reason", width=200)
        self.tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
        
        # === BUTTON FRAME ===
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Xem chi tiết", command=self.view_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Thay đổi trạng thái", command=self.change_status).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_appointment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.refresh_list).pack(side="left", padx=5)
        
        self.refresh_list()
    
    def refresh_list(self):
        """Làm mới danh sách lịch hẹn"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        appointments = self.controller.db.get_appointments()
        status_filter = self.status_var.get()
        
        for apt in appointments:
            if status_filter != "Tất cả" and apt["status"] != status_filter:
                continue
            
            patient_user = self.controller.db.get_user(apt["patient"])
            patient_name = patient_user["name"] if patient_user else apt["patient"]
            
            self.tree.insert("", "end", values=(
                apt["id"], patient_name, apt["date"], apt["time"], 
                apt["reason"][:50] if apt["reason"] else "", apt["status"]
            ))
    
    def get_selected_appointment(self):
        """Lấy lịch hẹn được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một lịch hẹn")
            return None
        return selection[0]
    
    def view_details(self):
        """Xem chi tiết lịch hẹn"""
        item_id = self.get_selected_appointment()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        apt_id = values[0]
        
        # Tìm appointment từ database
        appointments = self.controller.db.get_appointments()
        appointment = next((a for a in appointments if str(a["id"]) == apt_id), None)
        
        if not appointment:
            messagebox.showerror("Lỗi", "Không tìm thấy lịch hẹn")
            return
        
        patient_user = self.controller.db.get_user(appointment["patient"])
        patient_name = patient_user["name"] if patient_user else appointment["patient"]
        
        details = f"""
Thông tin lịch hẹn:
========================================
ID: {appointment['id']}
Bệnh nhân: {patient_name}
Ngày: {appointment['date']}
Giờ: {appointment['time']}
Lý do/Ghi chú: {appointment['reason']}
Trạng thái: {appointment['status']}
        """
        
        messagebox.showinfo("Chi tiết lịch hẹn", details)
    
    def change_status(self):
        """Thay đổi trạng thái lịch hẹn"""
        item_id = self.get_selected_appointment()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        apt_id = values[0]
        current_status = values[5]
        
        # Tạo cửa sổ chọn trạng thái
        change_win = tk.Toplevel(self)
        change_win.title("Thay đổi trạng thái")
        change_win.geometry("300x150")
        
        tk.Label(change_win, text=f"Trạng thái hiện tại: {current_status}", font=("Arial", 10)).pack(pady=10)
        ttk.Label(change_win, text="Trạng thái mới:").pack(pady=5)
        
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(change_win, textvariable=status_var,
                                    values=["Đã đặt", "Checked-in", "Hoan thanh", "Đã hủy"],
                                    state="readonly", width=25)
        status_combo.pack(pady=5, padx=20)
        
        def save_status():
            try:
                new_status = status_var.get()
                self.controller.db.cursor.execute(
                    "UPDATE appointments SET status = ? WHERE id = ?",
                    (new_status, apt_id)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật trạng thái thành công!")
                change_win.destroy()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Cập nhật thất bại: {str(e)}")
        
        ttk.Button(change_win, text="Lưu", command=save_status).pack(pady=15)
    
    def delete_appointment(self):
        """Xóa lịch hẹn"""
        item_id = self.get_selected_appointment()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        apt_id = values[0]
        patient_name = values[1]
        apt_date = values[2]
        apt_time = values[3]
        
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa lịch hẹn của {patient_name} vào {apt_date} lúc {apt_time}?"):
            try:
                self.controller.db.cursor.execute("DELETE FROM appointments WHERE id = ?", (apt_id,))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xóa lịch hẹn thành công!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")