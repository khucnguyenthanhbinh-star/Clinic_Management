import tkinter as tk
from tkinter import ttk, messagebox

class ExaminationView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="KHÁM BỆNH", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        # --- SỬA LỖI TẠI ĐÂY ---
        # Lấy danh sách bệnh nhân từ SQLite bằng hàm get_users_by_role
        patients = self.controller.db.get_users_by_role("patient")
        # patients là list các dict: [{'username': '...', 'name': '...'}, ...]
        patient_names = [p["name"] for p in patients]
        
        ttk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, pady=10, sticky="e")
        self.patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(frame, textvariable=self.patient_var, width=23)
        patient_combo['values'] = patient_names
        patient_combo.grid(row=0, column=1, pady=10)
        # -----------------------
        
        ttk.Label(frame, text="Chẩn đoán:").grid(row=1, column=0, pady=10, sticky="ne")
        self.diagnosis_text = tk.Text(frame, width=30, height=5)
        self.diagnosis_text.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Chỉ định xét nghiệm:").grid(row=2, column=0, pady=10, sticky="ne")
        self.test_text = tk.Text(frame, width=30, height=3)
        self.test_text.grid(row=2, column=1, pady=10)
        
        ttk.Button(frame, text="Lưu kết quả", command=self.save_examination).grid(row=3, column=0, columnspan=2, pady=20)

    def save_examination(self):
        # Hiện tại chưa có bảng lưu kết quả khám chi tiết trong DB mẫu, 
        # nên ta chỉ hiển thị thông báo thành công demo.
        patient = self.patient_var.get()
        diagnosis = self.diagnosis_text.get("1.0", "end-1c")
        
        if patient and diagnosis:
            messagebox.showinfo("Thành công", f"Đã lưu kết quả khám cho: {patient}")
            # Reset form
            self.patient_var.set("")
            self.diagnosis_text.delete("1.0", "end")
            self.test_text.delete("1.0", "end")
        else:
            messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân và nhập chẩn đoán")