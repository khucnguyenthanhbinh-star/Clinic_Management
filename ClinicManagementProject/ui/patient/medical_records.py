import tkinter as tk
from tkinter import ttk
import random
import json
import re
from datetime import datetime, timedelta

class MedicalRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.clinic_addresses = {
            "CS1": "Số 123 Cầu Giấy, Q. Cầu Giấy, TP. Hà Nội",
            "CS2": "Số 45 Hàng Bài, Q. Hoàn Kiếm, TP. Hà Nội",
            "CS3": "Số 88 Nguyễn Văn Linh, TP. Đà Nẵng"
        }
        self.default_address = "Trụ sở chính: TP. Hà Nội"

        # Layout chính
        self.paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)

        # === CỘT TRÁI: DANH SÁCH & BỘ LỌC ===
        left_frame = ttk.LabelFrame(self.paned, text="Danh sách hồ sơ", padding=10)
        self.paned.add(left_frame, width=380)

        # 1. BỘ LỌC NGÀY
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(filter_frame, text="Lọc theo:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Tất cả")
        self.cb_filter = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly", width=20)
        self.cb_filter['values'] = ["Tất cả", "30 ngày gần nhất", "6 tháng gần nhất", "Năm nay"]
        self.cb_filter.pack(side="left")
        self.cb_filter.bind("<<ComboboxSelected>>", self.load_history)

        # 2. DANH SÁCH
        self.tree = ttk.Treeview(left_frame, columns=("date", "doctor"), show="headings", selectmode="browse")
        self.tree.heading("date", text="Thời gian")
        self.tree.heading("doctor", text="Bác sĩ khám")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("doctor", width=200)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        # === CỘT PHẢI: CHI TIẾT ===
        self.right_frame = ttk.Frame(self.paned, style="PDF.TFrame")
        self.paned.add(self.right_frame)
        
        style = ttk.Style(); style.configure("PDF.TFrame", background="#525659")
        self.detail_content = tk.Canvas(self.right_frame, bg="#525659", highlightthickness=0)
        self.detail_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.detail_content.yview)
        
        self.paper = tk.Frame(self.detail_content, bg="white", padx=50, pady=50)
        self.detail_content.create_window((40, 20), window=self.paper, anchor="nw", width=750) 
        self.paper.bind("<Configure>", lambda e: self.detail_content.configure(scrollregion=self.detail_content.bbox("all")))
        
        self.detail_content.pack(side="left", fill="both", expand=True)
        self.detail_scrollbar.pack(side="right", fill="y")
        self.detail_content.configure(yscrollcommand=self.detail_scrollbar.set)

        self.load_history()

    def load_history(self, event=None):
        # Xóa danh sách cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        apts = self.controller.db.get_appointments(self.controller.auth.current_user)
        
        # Chỉ lấy những ca đã xong
        history_list = [apt for apt in apts if apt['status'] in ['Hoan thanh', 'Paid']]
        history_list.sort(key=lambda x: x['date'], reverse=True)
        
        # --- LOGIC LỌC NGÀY ---
        filter_type = self.filter_var.get()
        today = datetime.now().date()
        
        filtered_list = []
        for apt in history_list:
            try:
                apt_date = datetime.strptime(apt['date'], "%Y-%m-%d").date()
            except: continue

            is_valid = True
            if filter_type == "30 ngày gần nhất":
                if not (today - timedelta(days=30) <= apt_date <= today): is_valid = False
            elif filter_type == "6 tháng gần nhất":
                if not (today - timedelta(days=180) <= apt_date <= today): is_valid = False
            elif filter_type == "Năm nay":
                if apt_date.year != today.year: is_valid = False
            
            if is_valid:
                filtered_list.append(apt)

        # --- HIỂN THỊ ---
        for apt in filtered_list:
            raw_reason = apt['reason']
            doc_name = "Bác sĩ khám"
            
            # 1. Lấy từ cột doctor_username (Ưu tiên)
            d_user = apt.get('doctor_username')
            if d_user:
                u_obj = self.controller.db.get_user(d_user)
                if u_obj:
                    doc_name = u_obj['name']
            
            # 2. Nếu không có, parse từ text (Fallback)
            if doc_name == "Bác sĩ khám" and "]" in raw_reason:
                # Tìm chuỗi trong ngoặc vuông chứa BS hoặc ThS
                match = re.search(r'\[([^\]]*(?:BS|ThS)[^\]]*)\]', raw_reason)
                if match:
                    doc_name = match.group(1).strip()

            # Lưu ID vào tags để truy xuất lại khi click
            self.tree.insert("", "end", values=(apt['date'], doc_name), tags=(apt['id'],))

    def on_select_record(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        # Lấy ID từ tags
        apt_id = self.tree.item(selected[0])['tags'][0]
        
        # Tìm lại apt data đầy đủ từ DB
        all_apts = self.controller.db.get_appointments(self.controller.auth.current_user)
        apt = next((a for a in all_apts if str(a['id']) == str(apt_id)), None)
        
        if not apt: return
        
        date = apt['date']
        raw_reason = apt['reason']
        
        # --- CẬP NHẬT PHẦN NÀY ĐỂ LẤY TÊN BÁC SĨ CHÍNH XÁC ---
        doctor = "Bác sĩ khám"
        
        # 1. Thử lấy từ DB
        if apt.get('doctor_username'):
             u = self.controller.db.get_user(apt.get('doctor_username'))
             if u: doctor = u['name']
        
        # 2. Nếu vẫn là mặc định, thử lấy từ text trong ngoặc []
        if doctor == "Bác sĩ khám" and "]" in raw_reason:
            match = re.search(r'\[([^\]]*(?:BS|ThS)[^\]]*)\]', raw_reason)
            if match:
                doctor = match.group(1).strip()
        # -------------------------------------------------------

        # Làm sạch triệu chứng
        clean_symptom = re.sub(r'\[.*?\]', '', raw_reason).strip()
        stop_words = ["CHẨN ĐOÁN:", "CHỈ ĐỊNH:", "LỜI DẶN:", "KẾT LUẬN:", "ĐƠN THUỐC:"]
        for word in stop_words:
            if word in clean_symptom:
                clean_symptom = clean_symptom.split(word)[0].strip()
        
        if not clean_symptom: clean_symptom = "Khám sức khỏe định kỳ."
            
        self.render_medical_report(date, doctor, clean_symptom, raw_reason, apt_id)

    def render_medical_report(self, date, doctor, patient_symptom, raw_reason, apt_id):
        for w in self.paper.winfo_children(): w.destroy()

        addr = self.default_address
        if "[CS1]" in raw_reason: addr = self.clinic_addresses["CS1"]
        elif "[CS2]" in raw_reason: addr = self.clinic_addresses["CS2"]
        elif "[CS3]" in raw_reason: addr = self.clinic_addresses["CS3"]

        # Mock Data Logic
        data = {"exam": "", "diag": "", "treat": "", "pres": []}
        d_lower = doctor.lower()
        
        if "nhi" in d_lower or "liên" in d_lower:
            data["exam"] = "Họng đỏ, phổi thô."; data["diag"] = "J20 - Viêm phế quản cấp"; data["treat"] = "Kháng sinh, long đờm."
            data["pres"] = [("Augmentin 250", "14 Gói", "Sáng 1, Chiều 1"), ("Siro Prospan", "1 Chai", "Uống 5ml x 3")]
        elif "tim" in d_lower or "hùng" in d_lower:
            data["exam"] = "T1 T2 rõ. HA 150/90."; data["diag"] = "I10 - Tăng huyết áp"; data["treat"] = "Kiểm soát huyết áp."
            data["pres"] = [("Amlodipin 5mg", "30 Viên", "Sáng 1 viên"), ("Concor 2.5mg", "30 Viên", "Sáng 1 viên")]
        elif "da" in d_lower or "minh" in d_lower:
            data["exam"] = "Mẩn đỏ, ngứa."; data["diag"] = "L20 - Viêm da cơ địa"; data["treat"] = "Bôi thuốc, tránh xà phòng."
            data["pres"] = [("Fucidin H", "1 Tuýp", "Bôi da"), ("Telfast 180mg", "10 Viên", "Tối 1 viên")]
        else:
            data["exam"] = "Bụng mềm."; data["diag"] = "K29 - Viêm dạ dày"; data["treat"] = "Giảm tiết axit."
            data["pres"] = [("Nexium 40mg", "30 Viên", "Sáng 1 viên"), ("Phosphalugel", "20 Gói", "Uống khi đau")]

        # UI
        top = tk.Frame(self.paper, bg="white"); top.pack(fill="x", pady=10)
        
        # Căn giữa tên phòng khám
        tk.Label(top, text="PHÒNG KHÁM ĐA KHOA QUỐC TẾ", font=("Times", 16, "bold"), fg="#b71c1c", bg="white").pack()
        
        tk.Frame(self.paper, height=2, bg="black").pack(fill="x")
        tk.Label(self.paper, text=f"ĐC: {addr}", font=("Arial", 9, "italic"), bg="white").pack(pady=5)
        tk.Label(self.paper, text="PHIẾU KẾT QUẢ KHÁM BỆNH", font=("Arial", 20, "bold"), fg="#0d47a1", bg="white").pack(pady=15)

        inf = tk.Frame(self.paper, bg="white"); inf.pack(fill="x", padx=10)
        u = self.controller.db.get_user(self.controller.auth.current_user)
        self.line(inf, f"Họ tên: {u['name'].upper()}", f"Tuổi: 35", True)
        self.line(inf, f"Địa chỉ: {self.default_address}", f"Ngày khám: {date}")

        bd = tk.Frame(self.paper, bg="white"); bd.pack(fill="x", pady=20, padx=10)
        self.sect(bd, "1. Lý do đến khám:", patient_symptom)
        self.sect(bd, "2. Khám lâm sàng:", data["exam"])
        self.sect(bd, "3. Chẩn đoán:", data["diag"], True)
        self.sect(bd, "4. Hướng điều trị:", data["treat"])

        tk.Label(bd, text="5. Đơn thuốc:", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", pady=(15,5))
        tbl = tk.Frame(bd, bg="black", bd=1); tbl.pack(fill="x")
        h = tk.Frame(tbl, bg="#f0f0f0"); h.pack(fill="x", pady=1)
        for t,w in [("Tên thuốc", 40), ("SL", 10), ("Cách dùng", 30)]: tk.Label(h, text=t, width=w, font=("Arial",9,"bold"), bg="#f0f0f0").pack(side="left")

        for i, (m,q,u) in enumerate(data["pres"], 1):
            r = tk.Frame(tbl, bg="white"); r.pack(fill="x", pady=1)
            tk.Label(r, text=f"{i}. {m}", width=40, anchor="w", padx=5, bg="white").pack(side="left")
            tk.Label(r, text=q, width=10, bg="white", font=("Arial",9,"bold")).pack(side="left")
            tk.Label(r, text=u, width=30, anchor="w", bg="white").pack(side="left")

        ft = tk.Frame(self.paper, bg="white"); ft.pack(fill="x", pady=30)
        tk.Label(ft, text="* Tái khám khi hết thuốc.", font=("Arial", 10, "italic"), bg="white").pack(side="left")
        sig = tk.Frame(ft, bg="white"); sig.pack(side="right")
        tk.Label(sig, text="BÁC SĨ KHÁM BỆNH", font=("Arial", 11, "bold"), fg="#b71c1c", bg="white").pack()
        tk.Label(sig, text="\n\n", bg="white").pack()
        
        # HIỂN THỊ TÊN BÁC SĨ
        tk.Label(sig, text=doctor.upper(), font=("Arial", 11, "bold"), bg="white").pack()

    def line(self, p, t1, t2, b=False):
        f = tk.Frame(p, bg="white"); f.pack(fill="x", pady=2)
        font = ("Arial", 11, "bold") if b else ("Arial", 11)
        tk.Label(f, text=t1, font=font, bg="white", width=40, anchor="w").pack(side="left")
        tk.Label(f, text=t2, font=font, bg="white", anchor="w").pack(side="left")

    def sect(self, p, t, c, h=False):
        f = tk.Frame(p, bg="white"); f.pack(fill="x", pady=5)
        tk.Label(f, text=t, font=("Arial", 11, "bold"), bg="white", width=20, anchor="nw").pack(side="left")
        fg = "red" if h else "black"; font = "bold" if h else "normal"
        tk.Message(f, text=c, font=("Arial", 11, font), fg=fg, bg="white", width=500).pack(side="left")