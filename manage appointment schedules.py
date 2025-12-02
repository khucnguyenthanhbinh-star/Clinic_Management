import tkinter as tk
from tkinter import ttk, messagebox

# Dữ liệu mẫu
patients = [
    {"id": 1, "name": "Nguyen Van A"},
    {"id": 2, "name": "Tran Thi B"},
]

appointments = [
    {"id": 1, "patient_id": 1, "date": "2025-12-03"},
    {"id": 2, "patient_id": 2, "date": "2025-12-04"},
]

class AppointmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý lịch hẹn")
        self.setup_ui()
        self.load_appointments()

    def setup_ui(self):
        # Bảng lịch hẹn
        self.tree = ttk.Treeview(self.root, columns=("ID", "Bệnh nhân", "Ngày"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Bệnh nhân", text="Bệnh nhân")
        self.tree.heading("Ngày", text="Ngày")
        self.tree.pack(expand=1, fill="both")

        # Nút thêm và hủy lịch hẹn
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Hẹn mới", command=self.add_appointment).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Hủy lịch hẹn", command=self.delete_appointment).pack(side="left", padx=5)

    def load_appointments(self):
        # Xóa dữ liệu hiện tại
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Thêm dữ liệu
        for appt in appointments:
            patient_name = next((p["name"] for p in patients if p["id"] == appt["patient_id"]), "Unknown")
            self.tree.insert("", "end", values=(appt["id"], patient_name, appt["date"]))

    def add_appointment(self):
        def save():
            patient_index = patient_var.get()
            date = date_var.get().strip()
            if not patient_index or not date:
                messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân và nhập ngày!")
                return

            patient_id = patients[int(patient_index)]["id"]

            # Kiểm tra trùng lịch
            for appt in appointments:
                if appt["patient_id"] == patient_id and appt["date"] == date:
                    messagebox.showerror("Lỗi", "Bệnh nhân đã có lịch hẹn vào ngày này!")
                    return

            new_id = max([a["id"] for a in appointments], default=0) + 1
            appointments.append({"id": new_id, "patient_id": patient_id, "date": date})
            self.load_appointments()
            add_window.destroy()
            messagebox.showinfo("Thành công", "Tạo lịch hẹn thành công!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Hẹn lịch mới")

        tk.Label(add_window, text="Chọn bệnh nhân:").grid(row=0, column=0, padx=5, pady=5)
        patient_var = tk.StringVar()
        patient_options = [f"{p['name']}" for p in patients]
        patient_dropdown = ttk.Combobox(add_window, textvariable=patient_var, values=patient_options, state="readonly")
        patient_dropdown.grid(row=0, column=1, padx=5, pady=5)
        patient_dropdown.current(0)  # Mặc định chọn bệnh nhân đầu tiên

        tk.Label(add_window, text="Ngày hẹn (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        date_var = tk.StringVar()
        tk.Entry(add_window, textvariable=date_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Button(add_window, text="Lưu", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn lịch hẹn cần hủy!")
            return
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy lịch hẹn này?")
        if confirm:
            for item in selected:
                appt_id = self.tree.item(item)["values"][0]
                global appointments
                appointments = [a for a in appointments if a["id"] != appt_id]
            self.load_appointments()
            messagebox.showinfo("Thành công", "Đã hủy lịch hẹn!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppointmentManager(root)
    root.mainloop()
