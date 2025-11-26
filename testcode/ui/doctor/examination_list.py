import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class ExaminationListView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- HEADER ---
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="LỊCH KHÁM & DANH SÁCH CHỜ", font=("Arial", 16, "bold"), fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # --- MAIN LAYOUT (Chia đôi màn hình) ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # ================= CỘT TRÁI: DANH SÁCH BỆNH NHÂN HÔM NAY =================
        left_frame = ttk.LabelFrame(paned, text="Danh sách bệnh nhân", padding=10)
        paned.add(left_frame, width=550)

        # 1. Bộ lọc thời gian
        filter_frame = tk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="today")
        ttk.Radiobutton(filter_frame, text="Hôm nay", variable=self.filter_var, value="today", command=self.load_appointments).pack(side="left", padx=10)
        ttk.Radiobutton(filter_frame, text="Tuần này", variable=self.filter_var, value="week", command=self.load_appointments).pack(side="left", padx=10)
        
        ttk.Button(filter_frame, text="🔄 Làm mới", command=self.load_appointments).pack(side="right")

        # 2. Bảng danh sách
        cols = ("time", "name", "reason", "status")
        self.tree_queue = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree_queue.heading("time", text="Giờ")
        self.tree_queue.heading("name", text="Họ tên bệnh nhân")
        self.tree_queue.heading("reason", text="Lý do khám")
        self.tree_queue.heading("status", text="Trạng thái")
        
        self.tree_queue.column("time", width=60, anchor="center")
        self.tree_queue.column("name", width=150)
        self.tree_queue.column("reason", width=200)
        self.tree_queue.column("status", width=100, anchor="center")
        
        # Cấu hình màu sắc trạng thái (HIGHLIGHT QUAN TRỌNG)
        self.tree_queue.tag_configure("waiting", background="#fff3cd", foreground="#856404", font=("Arial", 10, "bold")) # Checked-in: Vàng cam đậm
        self.tree_queue.tag_configure("booked", foreground="#007bff") # Đã đặt: Xanh
        self.tree_queue.tag_configure("done", foreground="green") # Xong: Xanh lá
        self.tree_queue.tag_configure("cancel", foreground="gray") # Hủy: Xám

        self.tree_queue.pack(side="left", fill="both", expand=True)
        sb_queue = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_queue.yview)
        self.tree_queue.configure(yscrollcommand=sb_queue.set)
        sb_queue.pack(side="right", fill="y")
        
        # Sự kiện chọn bệnh nhân -> Load lịch sử
        self.tree_queue.bind("<<TreeviewSelect>>", self.on_patient_select)

        # ================= CỘT PHẢI: LỊCH SỬ KHÁM CỦA BỆNH NHÂN =================
        right_frame = ttk.LabelFrame(paned, text="Lịch sử khám bệnh (Hồ sơ cũ)", padding=10)
        paned.add(right_frame)

        self.lbl_history_info = tk.Label(right_frame, text="Chọn bệnh nhân bên trái để xem lịch sử", fg="gray", font=("Arial", 9, "italic"))
        self.lbl_history_info.pack(pady=(0, 10), anchor="w")

        cols_hist = ("date", "doctor", "diagnosis")
        self.tree_hist = ttk.Treeview(right_frame, columns=cols_hist, show="headings")
        
        self.tree_hist.heading("date", text="Ngày")
        self.tree_hist.heading("doctor", text="Bác sĩ khám")
        self.tree_hist.heading("diagnosis", text="Chẩn đoán / Kết luận")
        
        self.tree_hist.column("date", width=90)
        self.tree_hist.column("doctor", width=120)
        self.tree_hist.column("diagnosis", width=200)
        
        self.tree_hist.pack(fill="both", expand=True)

        # Load dữ liệu ban đầu
        self.load_appointments()

    def load_appointments(self):
        # Xóa dữ liệu cũ
        for item in self.tree_queue.get_children():
            self.tree_queue.delete(item)
            
        # Lấy bộ lọc thời gian
        mode = self.filter_var.get()
        today = datetime.now().date()
        
        # Lấy danh sách tất cả lịch hẹn
        # Lưu ý: Thực tế nên query DB có điều kiện WHERE date = ... để tối ưu
        all_apts = self.controller.db.get_appointments() 
        
        # Lấy thông tin bác sĩ đang đăng nhập
        current_doc_username = self.controller.auth.current_user
        current_doc_info = self.controller.db.get_user(current_doc_username)
        doc_name_check = current_doc_info['name'] # Dùng tên để filter nếu trong reason có lưu tên BS
        
        filtered_apts = []
        
        for apt in all_apts:
            try:
                apt_date = datetime.strptime(apt['date'], "%Y-%m-%d").date()
            except: continue

            # 1. Lọc theo thời gian
            if mode == "today":
                if apt_date != today: continue
            elif mode == "week":
                # Lấy tuần này (đơn giản hóa là 7 ngày tới và 7 ngày trước)
                if not (today <= apt_date <= today + timedelta(days=7)): continue

            # 2. Lọc theo Bác sĩ (Chỉ hiện bệnh nhân của mình)
            # Kiểm tra xem tên bác sĩ có trong lý do khám không (theo format [BS...])
            # Hoặc nếu hệ thống phân lịch cứng thì check doctor_id (nếu có)
            # Ở đây ta check lỏng: Nếu tên BS có trong reason HOẶC user là admin/test thì hiện hết
            if f"[{doc_name_check}]" not in apt['reason'] and "admin" not in current_doc_username:
                # Tạm thời comment dòng này để bạn dễ test nếu tên BS ko khớp 100%
                # continue 
                pass

            filtered_apts.append(apt)

        # 3. Sắp xếp theo giờ
        filtered_apts.sort(key=lambda x: x['time'])

        # 4. Hiển thị lên bảng
        for apt in filtered_apts:
            # Lấy tên bệnh nhân
            patient_user = self.controller.db.get_user(apt['patient'])
            p_name = patient_user['name'] if patient_user else apt['patient']
            
            # Xử lý lý do (cắt bỏ các mã code rườm rà)
            raw_reason = apt['reason']
            display_reason = raw_reason
            if "]" in raw_reason:
                display_reason = raw_reason.split("]")[-1].strip()

            status = apt['status']
            
            # Gán Tag màu sắc
            tag = ""
            if status == "Checked-in": tag = "waiting"   # QUAN TRỌNG: Đã đến
            elif status in ["Da dat", "Đã đặt", "Confirmed", "Unpaid"]: tag = "booked"
            elif status in ["Hoan thanh", "Paid"]: tag = "done"
            elif status in ["Da huy", "Đã hủy"]: tag = "cancel"

            # Lưu username bệnh nhân vào tags để truy vấn lịch sử
            self.tree_queue.insert("", "end", values=(apt['time'], p_name, display_reason, status), tags=(tag, apt['patient']))

    def on_patient_select(self, event):
        selected = self.tree_queue.selection()
        if not selected: return
        
        # Lấy username bệnh nhân từ tags
        item = self.tree_queue.item(selected[0])
        patient_username = item['tags'][1]
        patient_name = item['values'][1]
        
        self.lbl_history_info.config(text=f"Lịch sử khám của: {patient_name}", fg="#007bff")
        self.load_patient_history(patient_username)

    def load_patient_history(self, patient_username):
        # Xóa cũ
        for item in self.tree_hist.get_children():
            self.tree_hist.delete(item)
            
        # Lấy lịch sử
        apts = self.controller.db.get_appointments(patient_username)
        
        # Chỉ lấy những cái đã hoàn thành
        history = [a for a in apts if a['status'] in ['Hoan thanh', 'Paid']]
        history.sort(key=lambda x: x['date'], reverse=True) # Mới nhất lên đầu
        
        for h in history:
            # Parse tên bác sĩ và chẩn đoán
            raw = h['reason']
            doc = "BS Khám"
            diag = raw
            if "]" in raw:
                parts = raw.split("]")
                for p in parts:
                    if "BS" in p: doc = p.replace("[", "").strip()
                diag = parts[-1].strip()
                
            self.tree_hist.insert("", "end", values=(h['date'], doc, diag))