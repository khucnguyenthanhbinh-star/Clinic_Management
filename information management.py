import tkinter as tk
from tkinter import ttk, messagebox

# Dữ liệu mẫu
patients = [
    {"id": 1, "name": "Nguyen Van A", "age": 30, "history": "Tiểu đường"},
    {"id": 2, "name": "Tran Thi B", "age": 25, "history": "Huyết áp cao"},
]

appointments = [
    {"id": 1, "patient_id": 1, "date": "2025-12-03", "status": "Chưa khám"},
    {"id": 2, "patient_id": 2, "date": "2025-12-04", "status": "Chưa khám"},
]

class DoctorManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý thông tin bác sĩ")

        tab_control = ttk.Notebook(root)
        
        # Tab hồ sơ bệnh nhân
        self.patient_tab = ttk.Frame(tab_control)
        tab_control.add(self.patient_tab, text='Hồ sơ bệnh nhân')
        self.setup_patient_tab()

        # Tab lịch hẹn
        self.appointment_tab = ttk.Frame(tab_control)
        tab_control.add(self.appointment_tab, text='Lịch hẹn')
        self.setup_appointment_tab()

        tab_control.pack(expand=1, fill="both")

    def setup_patient_tab(self):
        # Danh sách bệnh nhân
        self.patient_tree = ttk.Treeview(self.patient_tab, columns=("ID", "Tên", "Tuổi", "Tiền sử"), show="headings")
        self.patient_tree.heading("ID", text="ID")
        self.patient_tree.heading("Tên", text="Tên")
        self.patient_tree.heading("Tuổi", text="Tuổi")
        self.patient_tree.heading("Tiền sử", text="Tiền sử bệnh")
        self.patient_tree.pack(expand=1, fill="both")
        self.load_patients()

        # Nút thêm bệnh nhân
        add_btn = tk.Button(self.patient_tab, text="Thêm bệnh nhân", command=self.add_patient)
        add_btn.pack(pady=5)

    def load_patients(self):
        for i in self.patient_tree.get_children():
            self.patient_tree.delete(i)
        for p in patients:
            self.patient_tree.insert("", "end", values=(p["id"], p["name"], p["age"], p["history"]))

    def add_patient(self):
        def save():
            new_id = max(p["id"] for p in patients) + 1 if patients else 1
            patients.append({"id": new_id, "name": name_var.get(), "age": int(age_var.get()), "history": history_var.get()})
            self.load_patients()
            add_window.destroy()
            messagebox.showinfo("Thành công", "Thêm bệnh nhân thành công!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm bệnh nhân")
        
        tk.Label(add_window, text="Tên:").grid(row=0, column=0)
        name_var = tk.StringVar()
        tk.Entry(add_window, textvariable=name_var).grid(row=0, column=1)
        
        tk.Label(add_window, text="Tuổi:").grid(row=1, column=0)
        age_var = tk.StringVar()
        tk.Entry(add_window, textvariable=age_var).grid(row=1, column=1)
        
        tk.Label(add_window, text="Tiền sử bệnh:").grid(row=2, column=0)
        history_var = tk.StringVar()
        tk.Entry(add_window, textvariable=history_var).grid(row=2, column=1)
        
        tk.Button(add_window, text="Lưu", command=save).grid(row=3, column=0, columnspan=2, pady=5)

    def setup_appointment_tab(self):
        self.appointment_tree = ttk.Treeview(self.appointment_tab, columns=("ID", "Bệnh nhân", "Ngày", "Trạng thái"), show="headings")
        self.appointment_tree.heading("ID", text="ID")
        self.appointment_tree.heading("Bệnh nhân", text="Bệnh nhân")
        self.appointment_tree.heading("Ngày", text="Ngày hẹn")
        self.appointment_tree.heading("Trạng thái", text="Trạng thái")
        self.appointment_tree.pack(expand=1, fill="both")
        self.load_appointments()

    def load_appointments(self):
        for i in self.appointment_tree.get_children():
            self.appointment_tree.delete(i)
        for a in appointments:
            patient_name = next((p["name"] for p in patients if p["id"] == a["patient_id"]), "Unknown")
            self.appointment_tree.insert("", "end", values=(a["id"], patient_name, a["date"], a["status"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = DoctorManager(root)
    root.mainloop()
