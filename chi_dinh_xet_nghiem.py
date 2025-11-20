import tkinter as tk
from tkinter import ttk, messagebox

class ClinicManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Phòng khám")
        self.root.geometry("1200x700")
        
        # Dữ liệu mẫu các xét nghiệm (có thể thay đổi)
        self.tests = ["Xét nghiệm máu", "Siêu âm bụng", "Chụp X-quang", "Xét nghiệm nước tiểu"]
        
        # Dữ liệu mẫu bác sĩ và bệnh nhân
        self.users = {
            "bs1": {"password": "123", "role": "doctor", "name": "BS. Nguyễn Văn A"},
            "bn1": {"password": "123", "role": "patient", "name": "Nguyễn Thị B"}
        }
        
        # Dữ liệu mẫu lịch hẹn
        self.appointments = [
            {"patient": "bn1", "date": "2025-11-20", "time": "09:00", "reason": "Đau bụng", "status": "Đã đặt"}
        ]
        
        self.create_main_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_screen(self):
        self.clear_screen()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Xin chào: {self.users['bs1']['name']}", font=("Arial", 12)).pack(side="left")
        ttk.Button(top_frame, text="Đăng xuất", command=self.clear_screen).pack(side="right")
        
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Menu
        menu_frame = ttk.LabelFrame(container, text="Menu", width=200)
        menu_frame.pack(side="left", fill="y", padx=5)
        menu_frame.pack_propagate(False)
        
        # Content
        self.content_frame = ttk.Frame(container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Tạo menu cho bác sĩ
        self.create_doctor_menu(menu_frame)

    def create_doctor_menu(self, parent):
        ttk.Button(parent, text="Chỉ định xét nghiệm", command=self.show_test_indication).pack(fill="x", pady=2)
        ttk.Button(parent, text="Danh sách khám", command=self.show_examination_list).pack(fill="x", pady=2)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_test_indication(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="CHỈ ĐỊNH XÉT NGHIỆM", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        # Chọn bệnh nhân
        ttk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, pady=10, sticky="e")
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(frame, textvariable=patient_var, width=23)
        patient_combo['values'] = [self.users[u]["name"] for u in self.users if self.users[u]["role"] == "patient"]
        patient_combo.grid(row=0, column=1, pady=10)
        
        # Nhập thông tin chẩn đoán
        ttk.Label(frame, text="Chẩn đoán:").grid(row=1, column=0, pady=10, sticky="ne")
        diagnosis_text = tk.Text(frame, width=30, height=3)
        diagnosis_text.grid(row=1, column=1, pady=10)
        
        # Chọn xét nghiệm
        ttk.Label(frame, text="Chọn xét nghiệm:").grid(row=2, column=0, pady=10, sticky="e")
        test_var = tk.StringVar()
        test_combo = ttk.Combobox(frame, textvariable=test_var, width=23)
        test_combo['values'] = self.tests  # Danh sách các xét nghiệm
        test_combo.grid(row=2, column=1, pady=10)
        
        # Danh sách các xét nghiệm đã chỉ định
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("patient", "diagnosis", "test"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("diagnosis", text="Chẩn đoán")
        tree.heading("test", text="Xét nghiệm")
        tree.pack(fill="both", expand=True)
        
        # Hàm thêm xét nghiệm vào danh sách
        def add_test():
            patient_name = patient_combo.get()
            diagnosis = diagnosis_text.get("1.0", "end-1c")
            test_name = test_var.get()
            
            if patient_name and diagnosis and test_name:
                tree.insert("", "end", values=(patient_name, diagnosis, test_name))
                patient_combo.set("")  # Xóa mục đã chọn
                diagnosis_text.delete("1.0", "end")  # Xóa phần chẩn đoán
                test_combo.set("")  # Xóa mục xét nghiệm đã chọn
        
        # Thêm xét nghiệm
        ttk.Button(frame, text="Thêm xét nghiệm", command=add_test).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Lưu chỉ định xét nghiệm (bác sĩ hoàn thành chỉ định)
        def save_test_indication():
            messagebox.showinfo("Thành công", "Đã lưu chỉ định xét nghiệm!")
            self.show_examination_list()  # Quay lại danh sách khám sau khi lưu chỉ định
        
        # Lưu chỉ định xét nghiệm
        ttk.Button(frame, text="Lưu chỉ định", command=save_test_indication).grid(row=4, column=0, columnspan=2, pady=20)

    def show_examination_list(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="DANH SÁCH KHÁM", font=("Arial", 16, "bold")).pack(pady=20)
        
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        tree = ttk.Treeview(tree_frame, columns=("patient", "date", "time", "reason"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("reason", text="Lý do")
        
        for apt in self.appointments:
            patient_name = self.users.get(apt["patient"], {}).get("name", apt["patient"])
            tree.insert("", "end", values=(patient_name, apt["date"], apt["time"], apt["reason"]))
        
        tree.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicManagementSystem(root)
    root.mainloop()
    