import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json

class PatientDashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username = self.controller.auth.current_user
        
        # --- 1. KHỞI TẠO DỮ LIỆU ---
        # Lấy thông tin User, Lịch hẹn, Hóa đơn từ Database ngay khi mở màn hình
        self.user_info = self.controller.db.get_user(self.username)
        self.appointments = self.controller.db.get_appointments(self.username)
        self.invoices = self.controller.db.get_all_patient_invoices(self.username)
        
        # --- 2. GIAO DIỆN HEADER ---
        self.create_header()

        # --- 3. GIAO DIỆN BODY ---
        self.body_frame = ttk.Frame(self)
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Kiểm tra điều kiện để hiện cảnh báo
        self.create_alerts()

        # Tìm và hiện lịch hẹn gần nhất
        self.create_upcoming_card()

        # Hiện thống kê và nút tắt
        self.create_stats_and_actions()

    def create_header(self):
        # Logic: Lấy giờ hiện tại để Chào (Sáng/Chiều/Tối)
        hour = datetime.now().hour
        if 5 <= hour < 12: greeting = "Chào buổi sáng"
        elif 12 <= hour < 18: greeting = "Chào buổi chiều"
        else: greeting = "Chào buổi tối"
        
        name = self.user_info['name']
        
        header_frame = tk.Frame(self, bg="white", height=80)
        header_frame.pack(fill="x")
        
        # Avatar hiển thị chữ cái đầu tên
        avt_char = name[0].upper() if name else "?"
        avt = tk.Label(header_frame, text=avt_char, font=("Arial", 24, "bold"), bg="#007bff", fg="white", width=3)
        avt.pack(side="left", padx=20, pady=10)
        
        txt_frame = tk.Frame(header_frame, bg="white")
        txt_frame.pack(side="left", fill="y", pady=10)
        
        tk.Label(txt_frame, text=f"{greeting}, {name}", font=("Arial", 16, "bold"), bg="white", fg="#333").pack(anchor="w")
        tk.Label(txt_frame, text="Chúc bạn có một ngày tốt lành.", font=("Arial", 10), bg="white", fg="gray").pack(anchor="w")

    def create_alerts(self):
        # Logic 1: Kiểm tra trường thiếu trong JSON Info
        try:
            info = json.loads(self.user_info['info'])
        except: info = {}
        
        missing = []
        if not info.get('phone'): missing.append("Số điện thoại")
        if not info.get('cccd'): missing.append("CCCD/CMND")
        
        if missing:
            alert = tk.Frame(self.body_frame, bg="#fff3cd", highlightbackground="#ffecb5", highlightthickness=1, padx=10, pady=10)
            alert.pack(fill="x", pady=(0, 10))
            tk.Label(alert, text="[CẢNH BÁO HỒ SƠ]", font=("Arial", 10, "bold"), bg="#fff3cd", fg="#856404").pack(side="left")
            tk.Label(alert, text=f"Bạn đang thiếu: {', '.join(missing)}. Vui lòng cập nhật ngay.", bg="#fff3cd", fg="#856404").pack(side="left", padx=10)
            ttk.Button(alert, text="Cập nhật", command=lambda: self.nav("update_info")).pack(side="right")

        # Logic 2: Kiểm tra hóa đơn Unpaid
        unpaid_count = len([i for i in self.invoices if i['status'] == 'Unpaid'])
        if unpaid_count > 0:
            debt = tk.Frame(self.body_frame, bg="#f8d7da", highlightbackground="#f5c6cb", highlightthickness=1, padx=10, pady=10)
            debt.pack(fill="x", pady=(0, 10))
            tk.Label(debt, text="[THANH TOÁN]", font=("Arial", 10, "bold"), bg="#f8d7da", fg="#721c24").pack(side="left")
            tk.Label(debt, text=f"Bạn có {unpaid_count} hóa đơn chưa thanh toán.", bg="#f8d7da", fg="#721c24").pack(side="left", padx=10)
            ttk.Button(debt, text="Thanh toán ngay", command=lambda: self.nav("payment")).pack(side="right")

    def create_upcoming_card(self):
        tk.Label(self.body_frame, text="Lịch hẹn sắp tới", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        card = ttk.LabelFrame(self.body_frame, padding=15)
        card.pack(fill="x", pady=(0, 20))
        
        # Logic: Lọc các lịch hẹn có ngày >= hôm nay và chưa hoàn thành
        today = datetime.now().strftime("%Y-%m-%d")
        upcoming = [a for a in self.appointments if a['date'] >= today and a['status'] in ["Da dat", "Đã đặt", "Unpaid", "Checked-in"]]
        
        # Sắp xếp để lấy cái gần nhất (theo ngày, sau đó theo giờ)
        upcoming.sort(key=lambda x: (x['date'], x['time'])) 
        
        if upcoming:
            apt = upcoming[0]
            
            # Lấy tên bác sĩ (từ cột doctor_username hoặc parse reason cũ)
            doc_name = "Bác sĩ"
            if apt.get('doctor_username'):
                u = self.controller.db.get_user(apt['doctor_username'])
                if u: doc_name = u['name']
            
            # Hiển thị
            row = tk.Frame(card)
            row.pack(fill="x")
            
            # Khối Ngày (Trái)
            date_obj = datetime.strptime(apt['date'], "%Y-%m-%d")
            day = date_obj.day
            month = date_obj.strftime("Tháng %m")
            
            # Đổi màu nếu là hôm nay
            is_today = (apt['date'] == today)
            bg_color = "#e3f2fd" if not is_today else "#ffebee" # Xanh hoặc Đỏ nhạt
            fg_color = "#0d47a1" if not is_today else "#b71c1c"
            status_text = "SẮP TỚI" if not is_today else "HÔM NAY"
            
            date_box = tk.Frame(row, bg=bg_color, width=80, height=70)
            date_box.pack(side="left", padx=(0, 15))
            date_box.pack_propagate(False)
            
            tk.Label(date_box, text=str(day), font=("Arial", 18, "bold"), bg=bg_color, fg=fg_color).pack(pady=(10, 0))
            tk.Label(date_box, text=month, font=("Arial", 10), bg=bg_color, fg=fg_color).pack()

            # Thông tin (Giữa)
            info_box = tk.Frame(row)
            info_box.pack(side="left", fill="both", expand=True)
            
            tk.Label(info_box, text=f"{apt['time']} - {doc_name}", font=("Arial", 12, "bold")).pack(anchor="w")
            
            # Làm sạch lý do (bỏ các thẻ [])
            reason_display = apt['reason']
            if "]" in reason_display:
                reason_display = reason_display.split("]")[-1].strip()
            
            tk.Label(info_box, text=f"Lý do: {reason_display}", fg="gray").pack(anchor="w")
            
            status_lbl = tk.Label(info_box, text=f"- {status_text}", font=("Arial", 9, "bold"), fg=fg_color)
            status_lbl.pack(anchor="w", pady=5)

            # Nút hành động (Phải)
            ttk.Button(row, text="Chi tiết", command=lambda: self.nav("appointment")).pack(side="right")
            
        else:
            # Không có lịch
            tk.Label(card, text="Bạn không có lịch hẹn nào sắp tới.", font=("Arial", 11), fg="gray").pack(pady=10)
            ttk.Button(card, text="+ Đặt lịch khám mới", command=lambda: self.nav("book")).pack()

    def create_stats_and_actions(self):
        f_container = tk.Frame(self.body_frame)
        f_container.pack(fill="x")
        
        # --- CỘT TRÁI: THỐNG KÊ ---
        stats_frame = ttk.LabelFrame(f_container, text="Hồ sơ sức khỏe", padding=10)
        stats_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Tính toán thống kê
        total_visits = len([a for a in self.appointments if a['status'] in ['Hoan thanh', 'Paid']])
        total_spent = sum([i['amount'] for i in self.invoices if i['status'] == 'Paid'])
        
        self.stat_row(stats_frame, "Tổng số lần khám:", f"{total_visits} lần")
        self.stat_row(stats_frame, "Tổng chi phí:", f"{total_spent:,.0f} đ")
        
        # Lần khám cuối cùng
        last_visit = "Chưa khám"
        completed = [a for a in self.appointments if a['status'] in ['Hoan thanh', 'Paid']]
        if completed:
            completed.sort(key=lambda x: x['date'], reverse=True)
            last_visit = completed[0]['date']
        self.stat_row(stats_frame, "Lần khám gần nhất:", last_visit)

        # --- CỘT PHẢI: LỐI TẮT (MENU NHANH) ---
        actions_frame = ttk.LabelFrame(f_container, text="Truy cập nhanh", padding=10)
        actions_frame.pack(side="left", fill="both", expand=True)
        
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        # Nút bấm không dùng icon
        self.btn_action(actions_frame, "Đặt lịch khám", lambda: self.nav("book"), 0, 0)
        self.btn_action(actions_frame, "Lịch sử khám", lambda: self.nav("history"), 0, 1)
        self.btn_action(actions_frame, "Thanh toán", lambda: self.nav("payment"), 1, 0)
        self.btn_action(actions_frame, "Hồ sơ cá nhân", lambda: self.nav("update_info"), 1, 1)

    def stat_row(self, parent, label, value):
        f = tk.Frame(parent); f.pack(fill="x", pady=2)
        tk.Label(f, text=label, fg="gray").pack(side="left")
        tk.Label(f, text=value, font=("Arial", 10, "bold")).pack(side="right")

    def btn_action(self, parent, text, cmd, r, c):
        btn = tk.Button(parent, text=text, font=("Arial", 10), bg="#f0f0f0", command=cmd, relief="groove", bd=1)
        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5, ipady=5)

    def nav(self, destination):
        # Điều hướng (Switch View)
        from ui.patient import book_appointment, view_appointments, medical_records, update_info, payment
        
        target = None
        if destination == "book": target = book_appointment.BookAppointmentView
        elif destination == "appointment": target = view_appointments.ViewAppointmentsView
        elif destination == "history": target = medical_records.MedicalRecordsView
        elif destination == "payment": target = payment.PaymentView
        elif destination == "update_info": target = update_info.UpdateInfoView
        
        if target:
            for w in self.master.winfo_children(): w.destroy()
            target(self.master, self.controller).pack(fill="both", expand=True)