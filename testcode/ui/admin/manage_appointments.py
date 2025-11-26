import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ManageAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ LỊCH HẸN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(filter_frame, text="Lọc trạng thái:").pack(side="left", padx=5)
        self.status_combo = ttk.Combobox(filter_frame, values=["Tất cả", "Da dat", "Hoan thanh", "Đã hủy"], state="readonly", width=15)
        self.status_combo.set("Tất cả")
        self.status_combo.pack(side="left", padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_appointments())
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Gán bác sĩ", command=self.assign_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Đổi trạng thái", command=self.change_status).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Hủy lịch", command=self.cancel_appointment).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("id", "patient", "date", "time", "doctor", "status"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("id", text="ID")
        self.tree.heading("patient", text="Bệnh nhân")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("doctor", text="Bác sĩ")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=40)
        self.tree.column("patient", width=120)
        self.tree.column("date", width=90)
        self.tree.column("time", width=60)
        self.tree.column("doctor", width=120)
        self.tree.column("status", width=90)
        self.tree.pack(fill="both", expand=True)
        
        self.appointments = []
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.appointments = self.controller.db.get_appointments()
        for apt in self.appointments:
            patient_user = self.controller.db.get_user(apt["patient"])
            patient_name = patient_user["name"] if patient_user else apt["patient"]
            doctor_name = "---"
            if apt.get("doctor"):
                doctor_user = self.controller.db.get_user(apt["doctor"])
                doctor_name = doctor_user["name"] if doctor_user else apt["doctor"]
            
            self.tree.insert("", "end", values=(
                apt["id"], patient_name, apt["date"], apt["time"], doctor_name, apt["status"]
            ), tags=(apt["id"],))

    def filter_appointments(self):
        status_filter = self.status_combo.get()
        self.tree.delete(*self.tree.get_children())
        
        for apt in self.appointments:
            if status_filter == "Tất cả" or apt["status"] == status_filter:
                patient_user = self.controller.db.get_user(apt["patient"])
                patient_name = patient_user["name"] if patient_user else apt["patient"]
                doctor_name = "---"
                if apt.get("doctor"):
                    doctor_user = self.controller.db.get_user(apt["doctor"])
                    doctor_name = doctor_user["name"] if doctor_user else apt["doctor"]
                
                self.tree.insert("", "end", values=(
                    apt["id"], patient_name, apt["date"], apt["time"], doctor_name, apt["status"]
                ), tags=(apt["id"],))

    def assign_doctor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch hẹn")
            return
        
        item = self.tree.item(selected[0])
        appointment_id = item["values"][0]
        
        # Find appointment
        apt = next((a for a in self.appointments if a["id"] == appointment_id), None)
        if not apt:
            messagebox.showerror("Lỗi", "Không tìm thấy lịch hẹn")
            return
        
        # Get list of doctors
        doctors = self.controller.db.get_users_by_role("doctor")
        doctor_names = {f"{doc['name']} ({doc['username']})": doc['username'] for doc in doctors}
        
        if not doctor_names:
            messagebox.showerror("Lỗi", "Không có bác sĩ trong hệ thống")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Gán bác sĩ")
        dialog.geometry("400x150")
        
        ttk.Label(dialog, text="Chọn bác sĩ:").pack(padx=10, pady=10)
        doctor_combo = ttk.Combobox(dialog, values=list(doctor_names.keys()), state="readonly", width=40)
        doctor_combo.pack(padx=10, pady=5)
        
        def assign():
            selected_doc = doctor_combo.get()
            if not selected_doc:
                messagebox.showerror("Lỗi", "Vui lòng chọn bác sĩ")
                return
            
            doctor_username = doctor_names[selected_doc]
            self.controller.db.assign_appointment_doctor(appointment_id, doctor_username)
            messagebox.showinfo("Thành công", "Đã gán bác sĩ")
            self.refresh_tree()
            dialog.destroy()
        
        ttk.Button(dialog, text="Gán", command=assign).pack(pady=10)

    def change_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch hẹn")
            return
        
        item = self.tree.item(selected[0])
        appointment_id = item["values"][0]
        
        dialog = tk.Toplevel(self)
        dialog.title("Đổi trạng thái")
        dialog.geometry("400x150")
        
        ttk.Label(dialog, text="Trạng thái mới:").pack(padx=10, pady=10)
        status_combo = ttk.Combobox(dialog, values=["Da dat", "Hoan thanh", "Đã hủy"], state="readonly", width=20)
        status_combo.pack(padx=10, pady=5)
        
        def update():
            new_status = status_combo.get()
            if not new_status:
                messagebox.showerror("Lỗi", "Vui lòng chọn trạng thái")
                return
            
            self.controller.db.update_appointment_status(appointment_id, new_status)
            messagebox.showinfo("Thành công", "Đã cập nhật trạng thái")
            self.refresh_tree()
            dialog.destroy()
        
        ttk.Button(dialog, text="Cập nhật", command=update).pack(pady=10)

    def cancel_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch hẹn")
            return
        
        item = self.tree.item(selected[0])
        appointment_id = item["values"][0]
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy lịch hẹn này?"):
            self.controller.db.cancel_appointment(appointment_id)
            messagebox.showinfo("Thành công", "Đã hủy lịch hẹn")
            self.refresh_tree()
