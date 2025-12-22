import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class ExaminationListView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_doctor = self.controller.auth.current_user # Lấy username bác sĩ đang đăng nhập
        
        # --- HEADER ---
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="LỊCH KHÁM CỦA TÔI", font=("Arial", 16, "bold"), fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # --- MAIN LAYOUT ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # TRÁI: DANH SÁCH
        left_frame = ttk.LabelFrame(paned, text=f"Danh sách bệnh nhân (BS {self.current_doctor})", padding=10)
        paned.add(left_frame, width=550)

        # Filter
        filter_frame = tk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        self.filter_var = tk.StringVar(value="today")
        ttk.Radiobutton(filter_frame, text="Hôm nay", variable=self.filter_var, value="today", command=self.load_appointments).pack(side="left", padx=10)
        ttk.Radiobutton(filter_frame, text="Tuần này", variable=self.filter_var, value="week", command=self.load_appointments).pack(side="left", padx=10)
        ttk.Button(filter_frame, text="🔄 Làm mới", command=self.load_appointments).pack(side="right")

        # Treeview
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
        
        # Tag màu
        self.tree_queue.tag_configure("waiting", background="#fff3cd", foreground="#856404", font=("Arial", 10, "bold"))
        self.tree_queue.tag_configure("booked", foreground="#007bff")
        self.tree_queue.tag_configure("done", foreground="green")
        self.tree_queue.tag_configure("cancel", foreground="gray")

        self.tree_queue.pack(side="left", fill="both", expand=True)
        sb_queue = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_queue.yview)
        self.tree_queue.configure(yscrollcommand=sb_queue.set)
        sb_queue.pack(side="right", fill="y")
        
        self.tree_queue.bind("<<TreeviewSelect>>", self.on_patient_select)

        # PHẢI: LỊCH SỬ
        right_frame = ttk.LabelFrame(paned, text="Lịch sử khám bệnh (Hồ sơ cũ)", padding=10)
        paned.add(right_frame)

        self.lbl_history_info = tk.Label(right_frame, text="Chọn bệnh nhân để xem lịch sử", fg="gray", font=("Arial", 9, "italic"))
        self.lbl_history_info.pack(pady=(0, 10), anchor="w")

        cols_hist = ("date", "doctor", "diagnosis")
        self.tree_hist = ttk.Treeview(right_frame, columns=cols_hist, show="headings")
        self.tree_hist.heading("date", text="Ngày")
        self.tree_hist.heading("doctor", text="Bác sĩ khám")
        self.tree_hist.heading("diagnosis", text="Kết luận")
        self.tree_hist.column("date", width=90)
        self.tree_hist.column("doctor", width=120)
        self.tree_hist.pack(fill="both", expand=True)

        self.load_appointments()

    def load_appointments(self):
        for item in self.tree_queue.get_children(): self.tree_queue.delete(item)
            
        mode = self.filter_var.get()
        today = datetime.now().date()
        all_apts = self.controller.db.get_appointments() 
        
        filtered_apts = []
        
        for apt in all_apts:
            # --- LOGIC QUAN TRỌNG: CHỈ LẤY CỦA MÌNH ---
            # Nếu doctor_username của lịch hẹn KHÁC với bác sĩ đang đăng nhập -> Bỏ qua
            if apt.get('doctor_username') and apt.get('doctor_username') != self.current_doctor:
                continue
            # ------------------------------------------

            try: apt_date = datetime.strptime(apt['date'], "%Y-%m-%d").date()
            except: continue

            if mode == "today":
                if apt_date != today: continue
            elif mode == "week":
                if not (today <= apt_date <= today + timedelta(days=7)): continue

            filtered_apts.append(apt)

        filtered_apts.sort(key=lambda x: x['time'])

        for apt in filtered_apts:
            user = self.controller.db.get_user(apt['patient'])
            p_name = user['name'] if user else apt['patient']
            
            raw_reason = apt['reason']
            display_reason = raw_reason
            if "]" in raw_reason:
                # Cắt lấy phần lý do cuối cùng
                display_reason = raw_reason.split("]")[-1].strip()

            status = apt['status']
            tag = ""
            if status == "Checked-in": tag = "waiting"
            elif status in ["Da dat", "Đã đặt", "Confirmed", "Unpaid"]: tag = "booked"
            elif status in ["Hoan thanh", "Paid"]: tag = "done"
            elif status in ["Da huy", "Đã hủy"]: tag = "cancel"

            self.tree_queue.insert("", "end", values=(apt['time'], p_name, display_reason, status), tags=(tag, apt['patient']))

    def on_patient_select(self, event):
        selected = self.tree_queue.selection()
        if not selected: return
        
        item = self.tree_queue.item(selected[0])
        patient_username = item['tags'][1]
        patient_name = item['values'][1]
        
        self.lbl_history_info.config(text=f"Lịch sử khám của: {patient_name}", fg="#007bff")
        self.load_patient_history(patient_username)

    def load_patient_history(self, patient_username):
        for item in self.tree_hist.get_children(): self.tree_hist.delete(item)
        apts = self.controller.db.get_appointments(patient_username)
        
        history = [a for a in apts if a['status'] in ['Hoan thanh', 'Paid']]
        history.sort(key=lambda x: x['date'], reverse=True)
        
        for h in history:
            doc_name = "Bác sĩ"
            if h.get('doctor_username'):
                u = self.controller.db.get_user(h['doctor_username'])
                if u: doc_name = u['name']
                
            # Lấy chẩn đoán từ reason (nếu có lưu format CHẨN ĐOÁN: ...)
            diag = h['reason']
            if "CHẨN ĐOÁN:" in diag:
                diag = diag.split("CHẨN ĐOÁN:")[1].split("\n")[0].strip()
            elif "]" in diag:
                diag = diag.split("]")[-1].strip()

            self.tree_hist.insert("", "end", values=(h['date'], doc_name, diag))