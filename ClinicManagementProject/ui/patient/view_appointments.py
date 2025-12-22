import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import random
import webbrowser
import urllib.parse

class ViewAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- TỪ ĐIỂN DỊCH TRẠNG THÁI ---
        self.STATUS_MAP = {
            "Da dat": "Đã đặt", "Đã đặt": "Đã đặt",
            "Unpaid": "Chưa thanh toán",
            "Hoan thanh": "Hoàn thành", "Paid": "Đã thanh toán",
            "Da huy": "Đã hủy", "Đã hủy": "Đã hủy",
            "Checked-in": "Đã check-in",
            "Confirmed": "Đã xác nhận"
        }
        
        self.raw_appointments = [] 

        # --- HEADER (ĐÃ SỬA TÊN THEO YÊU CẦU) ---
        header_frame = tk.Frame(self, bg="white", height=60)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="QUẢN LÝ LỊCH HẸN", font=("Arial", 16, "bold"), bg="white", fg="#007bff").pack(pady=15, padx=20, anchor="w")

        # --- MAIN CONTENT ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # === CỘT TRÁI ===
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, width=500)

        # 1. BỘ LỌC
        filter_frame = ttk.LabelFrame(left_frame, text="🔍 Bộ lọc tìm kiếm", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))

        # Dòng 1
        f_row1 = ttk.Frame(filter_frame)
        f_row1.pack(fill="x", pady=2)
        ttk.Label(f_row1, text="Thời gian:").pack(side="left")
        self.cb_date = ttk.Combobox(f_row1, values=["Tất cả", "Hôm nay", "7 ngày tới", "Tháng này", "Quá khứ"], state="readonly", width=12)
        self.cb_date.current(0)
        self.cb_date.pack(side="left", padx=(5, 15))

        ttk.Label(f_row1, text="Trạng thái:").pack(side="left")
        self.cb_status = ttk.Combobox(f_row1, values=["Tất cả", "Sắp tới/Chưa xong", "Hoàn thành/Đã trả", "Đã hủy"], state="readonly", width=18)
        self.cb_status.current(0)
        self.cb_status.pack(side="left", padx=5)

        # Dòng 2
        f_row2 = ttk.Frame(filter_frame)
        f_row2.pack(fill="x", pady=5)
        ttk.Label(f_row2, text="Bác sĩ:").pack(side="left")
        
        # Combobox Bác sĩ (Sẽ được nạp dữ liệu động từ lịch sử)
        self.cb_doctor = ttk.Combobox(f_row2, state="readonly", width=25)
        self.cb_doctor.pack(side="left", padx=(18, 5))
        
        ttk.Button(f_row2, text="Lọc ngay", command=self.apply_filters).pack(side="right")
        ttk.Button(f_row2, text="Xóa lọc", command=self.reset_filters).pack(side="right", padx=5)

        # 2. DANH SÁCH
        self.tree = self.create_treeview(left_frame)

        # === CỘT PHẢI ===
        self.right_frame = tk.Frame(paned, bg="white", relief="sunken", bd=1)
        paned.add(self.right_frame)
        
        self.lbl_placeholder = tk.Label(self.right_frame, text="Chọn một lịch hẹn để xem chi tiết", bg="white", fg="gray")
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.detail_container = tk.Frame(self.right_frame, bg="white")
        
        self.fetch_data_from_db()

    def create_treeview(self, parent):
        cols = ("id", "date", "time", "doctor", "status")
        tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tree.heading("id", text="Mã")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("doctor", text="Bác sĩ / Dịch vụ")
        tree.heading("status", text="Trạng thái")
        
        tree.column("id", width=50, anchor="center")
        tree.column("date", width=80, anchor="center")
        tree.column("time", width=60, anchor="center")
        tree.column("doctor", width=150)
        tree.column("status", width=110, anchor="center")
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Màu sắc
        tree.tag_configure("Da dat", foreground="#007bff"); tree.tag_configure("Đã đặt", foreground="#007bff")
        tree.tag_configure("Unpaid", foreground="red")     
        tree.tag_configure("Hoan thanh", foreground="green"); tree.tag_configure("Paid", foreground="green")
        tree.tag_configure("Da huy", foreground="gray"); tree.tag_configure("Đã hủy", foreground="gray")
        tree.tag_configure("Checked-in", foreground="#ffc107")
        
        return tree

    def fetch_data_from_db(self):
        # Lấy lịch sử của CHÍNH USER ĐANG ĐĂNG NHẬP
        apts = self.controller.db.get_appointments(self.controller.auth.current_user)
        self.raw_appointments = []
        
        # Set để lọc trùng tên bác sĩ
        doctors_set = set(["Tất cả"])

        for apt in apts:
            doc_name = "Bác sĩ"
            
            # Ưu tiên lấy từ cột doctor_username
            if apt.get('doctor_username'):
                u = self.controller.db.get_user(apt['doctor_username'])
                if u: doc_name = u['name']
            else:
                # Fallback: Parse từ reason (dành cho dữ liệu cũ)
                reason = apt['reason']
                if "[" in reason:
                    try:
                        parts = reason.split("]")
                        for p in parts:
                            if "BS" in p or "ThS" in p: doc_name = p.replace("[", "").strip()
                    except: pass
            
            # Thêm bác sĩ này vào danh sách bộ lọc
            doctors_set.add(doc_name)
            
            booking_code = f"#{apt['id']}"
            if "[" in apt['reason']:
                try: booking_code = apt['reason'].split("]")[0].replace("[", "")
                except: pass

            self.raw_appointments.append({
                "raw_data": apt,
                "display_doc": doc_name,
                "display_code": booking_code
            })

        # Cập nhật Combobox: Chỉ chứa các bác sĩ có trong set này
        self.cb_doctor['values'] = sorted(list(doctors_set))
        self.cb_doctor.current(0)
        
        self.apply_filters()

    def reset_filters(self):
        self.cb_date.current(0)
        self.cb_status.current(0)
        self.cb_doctor.current(0)
        self.apply_filters()

    def apply_filters(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        f_date = self.cb_date.get()
        f_status = self.cb_status.get()
        f_doctor = self.cb_doctor.get()
        today = datetime.now().date()
        
        for item in self.raw_appointments:
            apt = item['raw_data']
            try:
                apt_date = datetime.strptime(apt['date'], "%Y-%m-%d").date()
            except ValueError: continue

            raw_status = apt['status']
            
            # --- LỌC NGÀY ---
            match_date = True
            if f_date == "Hôm nay":
                if apt_date != today: match_date = False
            elif f_date == "7 ngày tới":
                if not (today <= apt_date <= today + timedelta(days=7)): match_date = False
            elif f_date == "Tháng này":
                if not (apt_date.month == today.month and apt_date.year == today.year): match_date = False
            elif f_date == "Quá khứ":
                if apt_date >= today: match_date = False

            # --- LỌC TRẠNG THÁI ---
            match_status = True
            is_upcoming = raw_status in ["Da dat", "Đã đặt", "Unpaid", "Checked-in", "Confirmed"]
            is_done = raw_status in ["Hoan thanh", "Paid", "Hoàn thành", "Đã thanh toán"]
            is_cancel = raw_status in ["Da huy", "Đã hủy"]
            
            if f_status == "Sắp tới/Chưa xong" and not is_upcoming: match_status = False
            elif f_status == "Hoàn thành/Đã trả" and not is_done: match_status = False
            elif f_status == "Đã hủy" and not is_cancel: match_status = False

            # --- LỌC BÁC SĨ ---
            match_doc = True
            if f_doctor != "Tất cả" and item['display_doc'] != f_doctor:
                match_doc = False

            if match_date and match_status and match_doc:
                display_status = self.STATUS_MAP.get(raw_status, raw_status)
                values = (item['display_code'], apt['date'], apt['time'], item['display_doc'], display_status)
                self.tree.insert("", "end", values=values, tags=(raw_status, apt['reason'], str(apt['id'])))

    # --- ACTIONS ---
    def on_select(self, event):
        selection = self.tree.selection()
        if not selection: return
        self.lbl_placeholder.place_forget()
        self.detail_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        item = self.tree.item(selection[0])
        vals = item['values']
        tags = item['tags']
        
        data = {
            "code": vals[0], "date": vals[1], "time": vals[2],
            "doctor": vals[3], "status_raw": tags[0],
            "reason": tags[1], "real_id": tags[2]
        }
        self.render_detail(data)

    def render_detail(self, data):
        for w in self.detail_container.winfo_children(): w.destroy()
        
        top = tk.Frame(self.detail_container, bg="white"); top.pack(fill="x")
        tk.Label(top, text="PHIẾU KHÁM ĐIỆN TỬ", font=("Arial", 10), bg="white", fg="gray").pack(anchor="w")
        tk.Label(top, text=f"MÃ SỐ: {data['code']}", font=("Arial", 18, "bold"), bg="white", fg="#007bff").pack(anchor="w")
        
        qr = tk.Frame(self.detail_container, bg="white", pady=10); qr.pack(fill="x")
        cv = tk.Canvas(qr, width=100, height=100, bg="white", highlightthickness=0); cv.pack(side="left")
        self.draw_fake_qr(cv)
        
        info_f = tk.Frame(qr, bg="white", padx=20); info_f.pack(side="left", fill="both", expand=True)
        tk.Label(info_f, text=f"Bác sĩ: {data['doctor']}", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(info_f, text=f"Thời gian: {data['time']} - {data['date']}", bg="white").pack(anchor="w")

        act = tk.Frame(self.detail_container, bg="white"); act.pack(fill="x", pady=20)
        
        st = data['status_raw']
        can_edit = st in ["Da dat", "Đã đặt", "Unpaid", "Checked-in"]
        
        if can_edit:
            ttk.Button(act, text="❌ Hủy lịch", command=lambda: self.action_cancel(data)).pack(side="left", padx=5)
        
        ttk.Button(act, text="Thêm vào Lịch", command=lambda: self.action_add_calendar(data)).pack(side="left", padx=5)

    def draw_fake_qr(self, cv):
        cv.delete("all"); sz = 8
        for r in range(12):
            for c in range(12): 
                if random.choice([True,False]): cv.create_rectangle(c*sz,r*sz,(c+1)*sz,(r+1)*sz, fill="black")

    def action_cancel(self, data):
        reason = simpledialog.askstring("Hủy", "Lý do hủy:", parent=self)
        if reason:
            if messagebox.askyesno("Xác nhận", "Bạn muốn hủy?"):
                self.controller.db.cancel_appointment(data['real_id'])
                messagebox.showinfo("OK", "Đã hủy.")
                self.fetch_data_from_db() 
                self.detail_container.pack_forget()

    def action_add_calendar(self, data):
        title = urllib.parse.quote(f"Kham: {data['doctor']}")
        url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={data['date'].replace('-','')}T080000/{data['date'].replace('-','')}T090000"
        webbrowser.open(url)