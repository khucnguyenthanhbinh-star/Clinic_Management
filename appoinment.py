import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class AppoinmentManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG QUẢN LÝ LỊCH HẸN PHÒNG KHÁM")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f4f8")

        # Dữ liệu
        self.doctors = ["BS. Nguyễn Văn A", "BS. Trần Thị B", "BS. Lê Văn C"]
        self.schedule = {}  # key: datetime, value: dict(patient, doctor, status)
        self.current_patient = "Bệnh nhân hiện tại"  # Demo, không cần đăng nhập

        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        # Tiêu đề chính
        title = tk.Label(self.root, text="QUẢN LÝ LỊCH HẸN", font=("Helvetica", 18, "bold"),
                         bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=15)

        # Chia 2 cột
        left_frame = tk.Frame(self.root, bg="#f0f4f8")
        left_frame.pack(side="left", padx=25, pady=10, fill="y")

        right_frame = tk.Frame(self.root, bg="#f0f4f8")
        right_frame.pack(side="right", padx=25, pady=10, fill="both", expand=True)

        # ==================== PHẦN BỆNH NHÂN ====================
        tk.Label(left_frame, text="BỆNH NHÂN ĐẶT LỊCH", font=("Arial", 14, "bold"),
                 bg="#f0f4f8", fg="#27ae60").pack(pady=10)

        # Chọn bác sĩ
        tk.Label(left_frame, text="Chọn bác sĩ:", bg="#f0f4f8").pack(anchor="w")
        self.doctor_combo = ttk.Combobox(left_frame, values=self.doctors, state="readonly", width=30)
        self.doctor_combo.set(self.doctors[0])
        self.doctor_combo.pack(pady=5)

        # Nhập ngày
        tk.Label(left_frame, text="Ngày khám (dd/mm/yyyy):", bg="#f0f4f8").pack(anchor="w")
        self.date_entry = tk.Entry(left_frame, width=33)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.date_entry.pack(pady=5)

        # Nút xem lịch trống
        tk.Button(left_frame, text="Xem lịch trống", bg="#3498db", fg="white",
                  command=self.show_available_slots).pack(pady=8)

        # Danh sách khung giờ
        tk.Label(left_frame, text="Khung giờ (chọn rồi nhấn Đặt lịch):", bg="#f0f4f8").pack(anchor="w")
        self.slots_list = tk.Listbox(left_frame, height=12, width=38)
        self.slots_list.pack(pady=5)

        # Nút đặt lịch
        tk.Button(left_frame, text="ĐẶT LỊCH", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                  command=self.book_appointment, height=2).pack(pady=10)

        # Nút hủy lịch
        tk.Button(left_frame, text="HỦY LỊCH ĐÃ CHỌN", bg="#e74c3c", fg="white",
                  command=self.cancel_appointment).pack(pady=5)

        # ==================== PHẦN BÁC SĨ & LỊCH CỦA BẠN ====================
        tk.Label(right_frame, text="LỊCH HẸN CỦA BẠN", font=("Arial", 12, "bold"),
                 bg="#f0f4f8", fg="#8e44ad").pack(pady=(20, 5))
        self.my_appointments_list = tk.Listbox(right_frame, height=10, width=60)
        self.my_appointments_list.pack(pady=5)

        tk.Label(right_frame, text="TẤT CẢ LỊCH KHÁM (Bác sĩ xem & xác nhận)",
                 font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#2980b9").pack(pady=(20, 5))
        self.all_appointments_list = tk.Listbox(right_frame, height=14, width=80)
        self.all_appointments_list.pack(pady=5)

        # Nút xác nhận cho bác sĩ
        tk.Button(right_frame, text="XÁC NHẬN LỊCH (Bác sĩ)", bg="#f39c12", fg="white",
                  font=("Arial", 10, "bold"), command=self.confirm_appointment,
                  width=30).pack(pady=10)

    # ==================== CÁC HÀM XỬ LÝ ====================
    def show_available_slots(self):
        doctor = self.doctor_combo.get()
        date_str = self.date_entry.get()
        try:
            day = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày không hợp lệ! Dùng định dạng dd/mm/yyyy")
            return

        self.slots_list.delete(0, tk.END)
        start = day.replace(hour=8, minute=0)
        for i in range(20):  # 8h00 -> 17h30, mỗi khung 30 phút
            slot_time = start + timedelta(minutes=i * 30)
            if slot_time.date() != day.date():
                break

            if slot_time not in self.schedule:
                self.slots_list.insert(tk.END, f"{slot_time.strftime('%H:%M')} - Trống")
            else:
                info = self.schedule[slot_time]
                self.slots_list.insert(tk.END, f"{slot_time.strftime('%H:%M')} - ĐÃ ĐẶT ({info['patient']})")

    def book_appointment(self):
        doctor = self.doctor_combo.get()
        date_str = self.date_entry.get()
        try:
            day = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày không hợp lệ!")
            return

        selection = self.slots_list.curselection()
        if not selection:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 khung giờ trống!")
            return

        time_str = self.slots_list.get(selection[0]).split(" - ")[0]
        chosen_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

        if chosen_time in self.schedule:
            messagebox.showerror("Lỗi", "Khung giờ này đã có người đặt!")
            return

        self.schedule[chosen_time] = {
            "patient": self.current_patient,
            "doctor": doctor,
            "status": "Đang chờ xác nhận"
        }
        messagebox.showinfo("Thành công",
                            f"Đặt lịch thành công!\n{doctor}\n{chosen_time.strftime('%d/%m/%Y %H:%M')}")
        self.show_available_slots()
        self.refresh_all()

    def cancel_appointment(self):
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy lịch đã chọn?"):
            return

        selection = self.my_appointments_list.curselection()
        if not selection:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lịch muốn hủy!")
            return

        line = self.my_appointments_list.get(selection[0])
        time_str = line.split(" | ")[0]
        time_obj = datetime.strptime(time_str, "%d/%m/%Y %H:%M")

        if time_obj in self.schedule and self.schedule[time_obj]["patient"] == self.current_patient:
            del self.schedule[time_obj]
            messagebox.showinfo("Thành công", "Đã hủy lịch hẹn!")
            self.refresh_all()

    def confirm_appointment(self):
        selection = self.all_appointments_list.curselection()
        if not selection:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lịch để xác nhận!")
            return

        line = self.all_appointments_list.get(selection[0])
        time_str = line.split(" | ")[0]
        time_obj = datetime.strptime(time_str, "%d/%m/%Y %H:%M")

        if time_obj in self.schedule:
            self.schedule[time_obj]["status"] = "Đã xác nhận"
            messagebox.showinfo("Thành công", "Đã xác nhận lịch hẹn!")
            self.refresh_all()

    def refresh_all(self):
        # Lịch của bệnh nhân hiện tại
        self.my_appointments_list.delete(0, tk.END)
        for time, info in sorted(self.schedule.items()):
            if info["patient"] == self.current_patient:
                self.my_appointments_list.insert(tk.END,
                    f"{time.strftime('%d/%m/%Y %H:%M')} | {info['doctor']} | {info['status']}")

        # Tất cả lịch hẹn
        self.all_appointments_list.delete(0, tk.END)
        for time, info in sorted(self.schedule.items()):
            self.all_appointments_list.insert(tk.END,
                f"{time.strftime('%d/%m/%Y %H:%M')} | {info['doctor']} | {info['patient']} | {info['status']}")


# ==================== CHẠY CHƯƠNG TRÌNH ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppoinmentManagement(root)
    root.mainloop()