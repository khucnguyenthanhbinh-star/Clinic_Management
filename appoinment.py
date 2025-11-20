import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Dữ liệu toàn cục
doctors = ["BS. Nguyễn Văn A", "BS. Trần Thị B", "BS. Lê Văn C"]
schedule = {}  # {datetime: {"patient": ..., "doctor": ..., "status": ...}}
current_patient = "Bệnh nhân hiện tại"  # Không cần đăng nhập, cố định tên để demo

# Tạo cửa sổ chính
root = tk.Tk()
root.title("HỆ THỐNG QUẢN LÝ LỊCH HẸN PHÒNG KHÁM")
root.geometry("900x600")
root.configure(bg="#f0f4f8")

# Tiêu đề
title = tk.Label(root, text="QUẢN LÝ LỊCH HẸN", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50")
title.pack(pady=15)

# Frame chính chia 2 cột
left_frame = tk.Frame(root, bg="#f0f4f8")
left_frame.pack(side="left", padx=20, pady=10, fill="y")

right_frame = tk.Frame(root, bg="#f0f4f8")
right_frame.pack(side="right", padx=20, pady=10, fill="both", expand=True)

# ==================== PHẦN BỆNH NHÂN ====================
tk.Label(left_frame, text="BỆNH NHÂN ĐẶT LỊCH", font=("Arial", 14, "bold"), bg="#f0f4f8", fg="#27ae60").pack(pady=10)

# Chọn bác sĩ
tk.Label(left_frame, text="Chọn bác sĩ:", bg="#f0f4f8").pack(anchor="w")
doctor_combo = ttk.Combobox(left_frame, values=doctors, state="readonly", width=30)
doctor_combo.set(doctors[0])
doctor_combo.pack(pady=5)

# Chọn ngày
tk.Label(left_frame, text="Ngày khám (dd/mm/yyyy):", bg="#f0f4f8").pack(anchor="w")
date_entry = tk.Entry(left_frame, width=33)
date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
date_entry.pack(pady=5)

# Nút xem lịch trống
def show_available_slots():
    doctor = doctor_combo.get()
    date_str = date_entry.get()
    try:
        day = datetime.strptime(date_str, "%d/%m/%Y")
    except:
        messagebox.showerror("Lỗi", "Ngày không hợp lệ! Dùng định dạng dd/mm/yyyy")
        return
    
    slots_list.delete(0, tk.END)
    start = day.replace(hour=8, minute=0)
    for i in range(20):
        slot_time = start + timedelta(minutes=i*30)
        if slot_time.date() != day.date():
            break
        key = slot_time
        if key not in schedule:
            slots_list.insert(tk.END, f"{slot_time.strftime('%H:%M')} - Trống")
        else:
            status = schedule[key]
            slots_list.insert(tk.END, f"{slot_time.strftime('%H:%M')} - ĐÃ ĐẶT ({status['patient']})")

tk.Button(left_frame, text="Xem lịch trống", bg="#3498db", fg="white", 
          command=show_available_slots).pack(pady=8)

# Danh sách khung giờ
tk.Label(left_frame, text="Khung giờ (chọn rồi nhấn Đặt lịch):", bg="#f0f4f8").pack(anchor="w")
slots_list = tk.Listbox(left_frame, height=12, width=35)
slots_list.pack(pady=5)

# Nút đặt lịch
def book_appointment():
    doctor = doctor_combo.get()
    date_str = date_entry.get()
    try:
        day = datetime.strptime(date_str, "%d/%m/%Y")
    except:
        messagebox.showerror("Lỗi", "Ngày không hợp lệ!")
        return
    
    selection = slots_list.curselection()
    if not selection:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 khung giờ trống!")
        return
    
    time_str = slots_list.get(selection[0]).split(" - ")[0]
    chosen_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
    
    if chosen_time in schedule:
        messagebox.showerror("Lỗi", "Khung giờ này đã có người đặt!")
        return
    
    schedule[chosen_time] = {
        "patient": current_patient,
        "doctor": doctor,
        "status": "Đang chờ xác nhận"
    }
    messagebox.showinfo("Thành công", f"Đặt lịch thành công!\n{doctor}\n{chosen_time.strftime('%d/%m/%Y %H:%M')}")
    show_available_slots()
    refresh_all()

tk.Button(left_frame, text="ĐẶT LỊCH", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
          command=book_appointment, height=2).pack(pady=10)

# Nút hủy lịch
def cancel_appointment():
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy lịch đã chọn?"):
        selection = my_appointments_list.curselection()
        if selection:
            idx = selection[0]
            time_str = my_appointments_list.get(idx).split(" | ")[0]
            time_obj = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
            if time_obj in schedule and schedule[time_obj]["patient"] == current_patient:
                del schedule[time_obj]
                messagebox.showinfo("Thành công", "Đã hủy lịch!")
                refresh_all()

tk.Button(left_frame, text="HỦY LỊCH ĐÃ CHỌN", bg="#e74c3c", fg="white",
          command=cancel_appointment).pack(pady=5)

# ==================== PHẦN BÁC Sĸ & LỊCH CỦA BẠN ====================
tk.Label(right_frame, text="LỊCH HẸN CỦA BẠN", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#8e44ad").pack(pady=(20,5))
my_appointments_list = tk.Listbox(right_frame, height=10, width=50)
my_appointments_list.pack(pady=5)

tk.Label(right_frame, text="TẤT CẢ LỊCH KHÁM (Bác sĩ xem & xác nhận)", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#2980b9").pack(pady=(20,5))
all_appointments_list = tk.Listbox(right_frame, height=12, width=70)
all_appointments_list.pack(pady=5)

# Nút xác nhận (dành cho bác sĩ)
def confirm_appointment():
    selection = all_appointments_list.curselection()
    if not selection:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn lịch để xác nhận!")
        return
    line = all_appointments_list.get(selection[0])
    time_str = line.split(" | ")[0]
    time_obj = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
    if time_obj in schedule:
        schedule[time_obj]["status"] = "Đã xác nhận"
        messagebox.showinfo("Thành công", "Đã xác nhận lịch hẹn!")
        refresh_all()

tk.Button(right_frame, text="XÁC NHẬN LỊCH (Bác sĩ)", bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
          command=confirm_appointment, width=30).pack(pady=10)

# Hàm làm mới danh sách
def refresh_all():
    # Lịch của bệnh nhân hiện tại
    my_appointments_list.delete(0, tk.END)
    for time, info in sorted(schedule.items()):
        if info["patient"] == current_patient:
            my_appointments_list.insert(tk.END, f"{time.strftime('%d/%m/%Y %H:%M')} | {info['doctor']} | {info['status']}")

    # Tất cả lịch (bác sĩ xem)
    all_appointments_list.delete(0, tk.END)
    for time, info in sorted(schedule.items()):
        status_color = "Đã xác nhận" if info["status"] == "Đã xác nhận" else "Chờ xác nhận"
        all_appointments_list.insert(tk.END, 
            f"{time.strftime('%d/%m/%Y %H:%M')} | {info['doctor']} | {info['patient']} | {info['status']}")

# Khởi động lần đầu
refresh_all()

# Chạy chương trình
root.mainloop()