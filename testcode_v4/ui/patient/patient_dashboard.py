import tkinter as tk
from tkinter import ttk
from datetime import datetime

class PatientDashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username = self.controller.auth.current_user
        
        # --- HEADER ---
        # Lấy tên thật từ DB
        user = self.controller.db.get_user(self.username)
        display_name = user['name']
        
        # Lấy giờ để chào (Sáng/Chiều/Tối)
        hour = datetime.now().hour
        greeting = "Chào buổi sáng" if 5 <= hour < 12 else ("Chào buổi chiều" if 12 <= hour < 18 else "Chào buổi tối")
        
        header_frame = tk.Frame(self, bg="#007bff", height=100)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text=f"{greeting}, {display_name}!", font=("Arial", 20, "bold"), bg="#007bff", fg="white").pack(pady=(20, 5), padx=20, anchor="w")
        tk.Label(header_frame, text="Chúc bạn một ngày nhiều sức khỏe.", font=("Arial", 12), bg="#007bff", fg="#e0e0e0").pack(pady=(0, 20), padx=20, anchor="w")

        # --- BODY ---
        body_frame = ttk.Frame(self)
        body_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. THẺ THÔNG BÁO QUAN TRỌNG (Lịch sắp tới)
        ttk.Label(body_frame, text="Lịch hẹn sắp tới", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        upcoming_frame = ttk.LabelFrame(body_frame, text=" Nhắc nhở ", padding=15)
        upcoming_frame.pack(fill="x", pady=(0, 20))
        
        # Tìm lịch hẹn gần nhất (Status = 'Da dat' hoặc 'Unpaid', Ngày >= Hôm nay)
        nearest_apt = self.get_nearest_appointment()
        
        if nearest_apt:
            # Parse thông tin
            date_str = nearest_apt['date']
            time_str = nearest_apt['time']
            reason = nearest_apt['reason']
            
            # Lấy tên bác sĩ từ reason (Hack chuỗi)
            doc_name = "Bác sĩ"
            if "]" in reason:
                parts = reason.split("]")
                for p in parts:
                    if "BS" in p or "ThS" in p: doc_name = p.replace("[", "").strip()

            # Giao diện thẻ lịch đẹp
            f1 = ttk.Frame(upcoming_frame)
            f1.pack(fill="x")
            
            # Cột ngày giờ (Nổi bật)
            date_box = tk.Label(f1, text=f"{time_str}\n{date_str}", bg="#e8f5e9", fg="#2e7d32", font=("Arial", 12, "bold"), padx=15, pady=10, relief="flat")
            date_box.pack(side="left", padx=(0, 15))
            
            # Cột thông tin
            info_box = ttk.Frame(f1)
            info_box.pack(side="left", fill="both", expand=True)
            
            ttk.Label(info_box, text=doc_name, font=("Arial", 12, "bold")).pack(anchor="w")
            ttk.Label(info_box, text=reason.split("]")[-1].strip(), font=("Arial", 10), foreground="gray").pack(anchor="w")
            
            ttk.Button(f1, text="Chi tiết", command=lambda: self.switch_to_manage()).pack(side="right")
        else:
            ttk.Label(upcoming_frame, text="Bạn không có lịch hẹn nào sắp tới.", font=("Arial", 11), foreground="gray").pack()
            ttk.Button(upcoming_frame, text="Đặt lịch ngay", command=lambda: self.switch_to_booking()).pack(pady=5)

        # 2. THỐNG KÊ NHANH
        stats_container = ttk.Frame(body_frame)
        stats_container.pack(fill="x")
        
        # Đếm số hóa đơn chưa trả
        unpaid_count = len(self.controller.db.get_unpaid_invoices(self.username))
        
        self.create_stat_card(stats_container, "Hóa đơn cần thanh toán", f"{unpaid_count}", "red" if unpaid_count > 0 else "green", 0)
        
        # Đếm tổng số lần đã khám
        all_apts = self.controller.db.get_appointments(self.username)
        done_count = len([a for a in all_apts if a['status'] in ['Hoan thanh', 'Paid']])
        self.create_stat_card(stats_container, "Lần khám thành công", f"{done_count}", "blue", 1)

    def get_nearest_appointment(self):
        apts = self.controller.db.get_appointments(self.username)
        today = datetime.now().strftime("%Y-%m-%d")
        
        upcoming = []
        for a in apts:
            if a['date'] >= today and a['status'] in ['Da dat', 'Unpaid']:
                upcoming.append(a)
        
        # Sort lấy ngày gần nhất
        upcoming.sort(key=lambda x: (x['date'], x['time']))
        return upcoming[0] if upcoming else None

    def create_stat_card(self, parent, title, value, color, col_idx):
        card = tk.Frame(parent, bg="white", highlightbackground="#cccccc", highlightthickness=1, padx=20, pady=15)
        card.grid(row=0, column=col_idx, padx=10, sticky="ew")
        parent.columnconfigure(col_idx, weight=1)
        
        tk.Label(card, text=value, font=("Arial", 24, "bold"), fg=color, bg="white").pack()
        tk.Label(card, text=title, font=("Arial", 10), fg="gray", bg="white").pack()

    # Hàm chuyển hướng (Hack switch view)
    def switch_to_booking(self):
        from ui.patient.book_appointment import BookAppointmentView
        for w in self.master.winfo_children(): w.destroy()
        BookAppointmentView(self.master, self.controller).pack(fill="both", expand=True)

    def switch_to_manage(self):
        from ui.patient.view_appointments import ViewAppointmentsView
        for w in self.master.winfo_children(): w.destroy()
        ViewAppointmentsView(self.master, self.controller).pack(fill="both", expand=True)