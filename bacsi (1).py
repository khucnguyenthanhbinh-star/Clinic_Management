import tkinter as tk
from tkinter import ttk, messagebox

class DoctorPanel:
    def __init__(self, root, users, appointments, medicines):
        self.root = root
        self.users = users
        self.appointments = appointments
        self.medicines = medicines
        self.current_patient = None
        self.patient_history = {}  # Lưu lịch sử khám bệnh
        self.create_main_screen()

    def clear_content(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_screen(self):
        self.clear_content()
        tk.Label(self.root, text="BẢNG ĐIỀU KHIỂN BÁC SĨ", font=("Arial", 16, "bold")).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Danh sách bệnh nhân cần khám", width=30, command=self.show_examination_list).pack(pady=5)
        tk.Button(frame, text="Khám bệnh", width=30, command=self.show_examination).pack(pady=5)
        tk.Button(frame, text="Kê đơn thuốc", width=30, command=self.show_prescription).pack(pady=5)
        tk.Button(frame, text="Xem hồ sơ bệnh nhân", width=30, command=self.show_patient_records).pack(pady=5)

    def show_examination_list(self):
        self.clear_content()
        tk.Label(self.root, text="DANH SÁCH BỆNH NHÂN CẦN KHÁM", font=("Arial", 14, "bold")).pack(pady=10)

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("patient", "date", "time", "reason"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("reason", text="Lý do")

        for apt in self.appointments:
            patient_name = self.users.get(apt["patient"], {}).get("name", apt["patient"])
            tree.insert("", "end", values=(patient_name, apt["date"], apt["time"], apt["reason"]))

        tree.pack(fill="both", expand=True)
        tk.Button(self.root, text="Quay lại", command=self.create_main_screen).pack(pady=10)

    def show_examination(self):
        self.clear_content()
        tk.Label(self.root, text="KHÁM BỆNH", font=("Arial", 14, "bold")).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Chọn bệnh nhân:").grid(row=0, column=0, sticky="e")
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(frame, textvariable=patient_var, width=25)
        patient_combo['values'] = [self.users[u]["name"] for u in self.users if self.users[u]["role"] == "patient"]
        patient_combo.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Chẩn đoán:").grid(row=1, column=0, sticky="ne")
        diagnosis_text = tk.Text(frame, width=30, height=5)
        diagnosis_text.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Chỉ định xét nghiệm:").grid(row=2, column=0, sticky="ne")
        test_text = tk.Text(frame, width=30, height=3)
        test_text.grid(row=2, column=1, pady=5)

        def save_examination():
            patient = patient_var.get()
            diagnosis = diagnosis_text.get("1.0", "end-1c")
            tests = test_text.get("1.0", "end-1c")
            if patient:
                self.patient_history.setdefault(patient, []).append({
                    "diagnosis": diagnosis,
                    "tests": tests
                })
                messagebox.showinfo("Thành công", f"Đã lưu kết quả khám cho {patient}")
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân")

        tk.Button(frame, text="Lưu kết quả", command=save_examination).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Quay lại", command=self.create_main_screen).pack(pady=10)

    def show_prescription(self):
        self.clear_content()
        tk.Label(self.root, text="KÊ ĐƠN THUỐC", font=("Arial", 14, "bold")).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Chọn thuốc:").grid(row=0, column=0, sticky="e")
        medicine_var = tk.StringVar()
        medicine_combo = ttk.Combobox(frame, textvariable=medicine_var, values=list(self.medicines.keys()), width=25)
        medicine_combo.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Số lượng:").grid(row=1, column=0, sticky="e")
        quantity_entry = tk.Entry(frame, width=27)
        quantity_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Hướng dẫn:").grid(row=2, column=0, sticky="ne")
        instruction_text = tk.Text(frame, width=30, height=3)
        instruction_text.grid(row=2, column=1, pady=5)

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("medicine", "quantity", "instruction"), show="headings")
        tree.heading("medicine", text="Thuốc")
        tree.heading("quantity", text="Số lượng")
        tree.heading("instruction", text="Hướng dẫn")
        tree.pack(fill="both", expand=True)

        def add_medicine():
            med = medicine_var.get()
            qty = quantity_entry.get()
            instr = instruction_text.get("1.0", "end-1c")
            if med and qty:
                tree.insert("", "end", values=(med, qty, instr))
                medicine_combo.set("")
                quantity_entry.delete(0, "end")
                instruction_text.delete("1.0", "end")

        tk.Button(frame, text="Thêm thuốc", command=add_medicine).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Quay lại", command=self.create_main_screen).pack(pady=10)

    def show_patient_records(self):
        self.clear_content()
        tk.Label(self.root, text="HỒ SƠ BỆNH NHÂN", font=("Arial", 14, "bold")).pack(pady=10)

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("patient", "diagnosis", "tests"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("diagnosis", text="Chẩn đoán")
        tree.heading("tests", text="Xét nghiệm")

        for patient, records in self.patient_history.items():
            for rec in records:
                tree.insert("", "end", values=(patient, rec["diagnosis"], rec["tests"]))

        tree.pack(fill="both", expand=True)
        tk.Button(self.root, text="Quay lại", command=self.create_main_screen).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    # Dữ liệu giả lập
    users = {
        "bn1": {"role": "patient", "name": "Nguyễn Thị B"},
        "bn2": {"role": "patient", "name": "Trần Văn C"},
        "bn3": {"role": "patient", "name": "Lê Thị D"},
    }
    appointments = [
        {"patient": "bn1", "date": "2025-11-26", "time": "09:00", "reason": "Sốt"},
        {"patient": "bn2", "date": "2025-11-26", "time": "10:00", "reason": "Ho"}
    ]
    medicines = {"Paracetamol": {"quantity": 100, "unit": "viên"}, "Amoxicillin": {"quantity": 50, "unit": "viên"}}

    app = DoctorPanel(root, users, appointments, medicines)
    root.mainloop()
