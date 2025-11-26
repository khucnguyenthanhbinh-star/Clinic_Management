import tkinter as tk
from tkinter import ttk
import random
import json

class MedicalRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Địa chỉ phòng khám
        self.clinic_addresses = {
            "CS1": "Số 123 Cầu Giấy, Q. Cầu Giấy, TP. Hà Nội",
            "CS2": "Số 45 Hàng Bài, Q. Hoàn Kiếm, TP. Hà Nội",
            "CS3": "Số 88 Nguyễn Văn Linh, TP. Đà Nẵng"
        }
        self.default_address = "Trụ sở chính: TP. Hà Nội"

        # Layout
        self.paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- TRÁI: DANH SÁCH ---
        left_frame = ttk.LabelFrame(self.paned, text="Danh sách hồ sơ", padding=10)
        self.paned.add(left_frame, width=380)

        self.tree = ttk.Treeview(left_frame, columns=("date", "doctor"), show="headings", selectmode="browse")
        self.tree.heading("date", text="Thời gian")
        self.tree.heading("doctor", text="Bác sĩ / Chuyên khoa")
        self.tree.column("date", width=100)
        self.tree.column("doctor", width=200)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        # --- PHẢI: PHIẾU KHÁM ---
        self.right_frame = ttk.Frame(self.paned, style="White.TFrame")
        self.paned.add(self.right_frame)

        style = ttk.Style()
        style.configure("White.TFrame", background="#525659") # Màu nền tối giống trình đọc PDF
        
        # Canvas mô phỏng tờ giấy A4
        self.detail_content = tk.Canvas(self.right_frame, bg="#525659", highlightthickness=0)
        self.detail_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.detail_content.yview)
        
        # Tờ giấy trắng A4 nằm giữa
        self.paper = tk.Frame(self.detail_content, bg="white", padx=50, pady=50)
        
        self.detail_content.create_window((40, 20), window=self.paper, anchor="nw", width=750) 
        
        # Update scroll region
        self.paper.bind("<Configure>", lambda e: self.detail_content.configure(scrollregion=self.detail_content.bbox("all")))
        self.detail_content.configure(yscrollcommand=self.detail_scrollbar.set)
        
        self.detail_content.pack(side="left", fill="both", expand=True)
        self.detail_scrollbar.pack(side="right", fill="y")

        self.load_history()

    def load_history(self):
        appointments = self.controller.db.get_appointments(self.controller.auth.current_user)
        # Lọc lịch sử đã xong
        history_list = [apt for apt in appointments if apt['status'] in ['Hoan thanh', 'Paid']]
        history_list.sort(key=lambda x: x['date'], reverse=True)
        
        for apt in history_list:
            raw_reason = apt['reason']
            doc_name = "Bác sĩ khám"
            # Tách tên bác sĩ từ chuỗi lý do
            if "]" in raw_reason:
                parts = raw_reason.split("]")
                for p in parts:
                    if "BS" in p or "ThS" in p: 
                        doc_name = p.replace("[", "").strip()
            
            self.tree.insert("", "end", values=(apt['date'], doc_name), tags=(raw_reason, doc_name))

    def on_select_record(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        date, doctor = item['values']
        raw_reason = item['tags'][0]
        
        # Lấy lý do khám ban đầu của bệnh nhân (phần cuối chuỗi)
        patient_symptom = raw_reason.split("]")[-1].strip()
        
        self.render_medical_report(date, doctor, patient_symptom, raw_reason)

    def render_medical_report(self, date, doctor, patient_symptom, raw_reason):
        for widget in self.paper.winfo_children(): widget.destroy()

        # 1. Xử lý địa chỉ
        current_address = self.default_address
        if "[CS1]" in raw_reason: current_address = self.clinic_addresses["CS1"]
        elif "[CS2]" in raw_reason: current_address = self.clinic_addresses["CS2"]
        elif "[CS3]" in raw_reason: current_address = self.clinic_addresses["CS3"]

        # 2. DỮ LIỆU Y KHOA GIẢ LẬP (MEDICAL MOCK DATA)
        # Tạo chẩn đoán chuyên nghiệp dựa trên tên/chuyên khoa của bác sĩ
        
        medical_data = {
            "symptoms": patient_symptom, # Triệu chứng bệnh nhân khai
            "exam_result": "",           # Khám lâm sàng
            "diagnosis": "",             # Chẩn đoán xác định (ICD-10)
            "treatment": "",             # Hướng điều trị
            "prescription": []           # Đơn thuốc
        }

        # Logic sinh dữ liệu theo chuyên khoa
        if "Nhi" in doctor or "Lien" in doctor:
            medical_data["exam_result"] = "Họng đỏ, amidan sưng độ 2. Phổi thô, có ran ẩm rải rác."
            medical_data["diagnosis"] = "J20 - Viêm phế quản cấp (Acute Bronchitis)"
            medical_data["treatment"] = "Kháng sinh, long đờm, hạ sốt, vệ sinh mũi họng."
            medical_data["prescription"] = [
                ("Augmentin 250mg", "10 Gói", "Ngày uống 2 lần, mỗi lần 1 gói sau ăn"),
                ("Siro Prospan", "1 Chai", "Uống 5ml x 3 lần/ngày"),
                ("Alpha Choay", "20 Viên", "Ngậm dưới lưỡi 2 viên/ngày"),
                ("Oresol 245", "5 Gói", "Pha 200ml nước, uống thay nước lọc")
            ]
        
        elif "Tim" in doctor or "Hung" in doctor:
            medical_data["exam_result"] = "T1, T2 đều, rõ. Huyết áp 150/90 mmHg. Tim nhịp xoang 90 l/p."
            medical_data["diagnosis"] = "I10 - Tăng huyết áp vô căn (Primary Hypertension)"
            medical_data["treatment"] = "Kiểm soát huyết áp, thay đổi lối sống, giảm mặn."
            medical_data["prescription"] = [
                ("Amlodipin 5mg", "30 Viên", "Sáng 1 viên"),
                ("Concor 2.5mg", "30 Viên", "Sáng 1 viên"),
                ("Panangin", "60 Viên", "Sáng 1 viên, Chiều 1 viên"),
                ("Aspirin 81mg", "30 Viên", "Trưa 1 viên sau ăn no")
            ]

        elif "Da" in doctor or "Minh" in doctor or "Hoa" in doctor:
            medical_data["exam_result"] = "Da vùng lưng có mảng đỏ, mụn nước tập trung thành đám, ranh giới rõ."
            medical_data["diagnosis"] = "L20 - Viêm da cơ địa dị ứng (Atopic Dermatitis)"
            medical_data["treatment"] = "Bôi thuốc, uống chống dị ứng, tránh xà phòng hóa chất."
            medical_data["prescription"] = [
                ("Fucidin H", "1 Tuýp", "Bôi sáng - tối vào vùng da bệnh"),
                ("Telfast 180mg", "10 Viên", "Tối uống 1 viên"),
                ("Vitamin C 500mg", "20 Viên", "Sáng 1 viên sau ăn"),
                ("Cetaphil Cleanser", "1 Chai", "Dùng tắm rửa hàng ngày")
            ]
            
        else: # Nội tổng quát / Mặc định
            medical_data["exam_result"] = "Bụng mềm, ấn đau vùng thượng vị. Ợ hơi, ợ chua."
            medical_data["diagnosis"] = "K29 - Viêm dạ dày trào ngược (GERD)"
            medical_data["treatment"] = "Giảm tiết axit, trung hòa dịch vị, men tiêu hóa."
            medical_data["prescription"] = [
                ("Nexium 40mg", "30 Viên", "Uống 1 viên trước ăn sáng 30p"),
                ("Phosphalugel (Chữ P)", "20 Gói", "Uống khi đau hoặc sau ăn"),
                ("Domperidon 10mg", "20 Viên", "Uống trước ăn 15p"),
                ("Vitamin 3B", "30 Viên", "Sáng 1 viên")
            ]

        # --- VẼ GIAO DIỆN PHIẾU ---
        
        # 1. Header
        top_f = tk.Frame(self.paper, bg="white")
        top_f.pack(fill="x", pady=10)
        
        # Logo/Tên (Trái)
        tk.Label(top_f, text="PHÒNG KHÁM ĐA KHOA QUỐC TẾ", font=("Times New Roman", 16, "bold"), fg="#b71c1c", bg="white").pack(side="left")
        # Mã phiếu (Phải)
        tk.Label(top_f, text=f"Mã BA: {random.randint(100000,999999)}", font=("Arial", 10), bg="white").pack(side="right")
        
        tk.Frame(self.paper, height=2, bg="black").pack(fill="x") # Line kẻ ngang
        
        tk.Label(self.paper, text=f"ĐC: {current_address}", font=("Arial", 9, "italic"), bg="white").pack(pady=5)
        
        tk.Label(self.paper, text="PHIẾU KẾT QUẢ KHÁM BỆNH", font=("Arial", 20, "bold"), fg="#0d47a1", bg="white").pack(pady=20)

        # 2. Hành chính
        info_box = tk.Frame(self.paper, bg="white")
        info_box.pack(fill="x", padx=10)
        
        user = self.controller.db.get_user(self.controller.auth.current_user)
        name = user['name'].upper()
        # Giả lập tuổi
        age = str(2025 - 1990) 
        
        self.add_line(info_box, f"Họ và tên: {name}", f"Tuổi: {age}", is_bold=True)
        self.add_line(info_box, f"Địa chỉ: {self.default_address}", f"Giới tính: Nam")
        self.add_line(info_box, f"Đối tượng: Thu phí", f"Ngày khám: {date}")

        # 3. Chuyên môn
        body = tk.Frame(self.paper, bg="white")
        body.pack(fill="x", pady=20, padx=10)
        
        self.add_section(body, "1. Lý do đến khám:", medical_data["symptoms"])
        self.add_section(body, "2. Khám lâm sàng:", medical_data["exam_result"])
        self.add_section(body, "3. Chẩn đoán xác định:", medical_data["diagnosis"], highlight=True)
        self.add_section(body, "4. Hướng điều trị:", medical_data["treatment"])

        # 4. Đơn thuốc (Kẻ bảng)
        tk.Label(body, text="5. Chỉ định dùng thuốc:", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", pady=(15, 5))
        
        table = tk.Frame(body, bg="black", bd=1)
        table.pack(fill="x")
        
        # Header
        cols = [("STT", 5), ("Tên thuốc / Hàm lượng", 35), ("ĐVT", 10), ("Số lượng", 10), ("Cách dùng", 30)]
        h_frame = tk.Frame(table, bg="#f0f0f0")
        h_frame.pack(fill="x", pady=1) # Gap 1px tạo đường kẻ
        for txt, w in cols:
            tk.Label(h_frame, text=txt, width=w, font=("Arial", 9, "bold"), bg="#f0f0f0").pack(side="left", fill="y")

        # Rows
        for idx, (med, qty_txt, use) in enumerate(medical_data["prescription"], 1):
            # Tách số lượng và đơn vị giả lập
            unit = "Viên" if "Viên" in qty_txt else ("Chai" if "Chai" in qty_txt else "Gói")
            qty_num = qty_txt.replace(unit, "").strip()
            
            r_frame = tk.Frame(table, bg="white")
            r_frame.pack(fill="x", pady=1)
            
            tk.Label(r_frame, text=str(idx), width=5, bg="white").pack(side="left")
            tk.Label(r_frame, text=med, width=35, bg="white", anchor="w", padx=5).pack(side="left")
            tk.Label(r_frame, text=unit, width=10, bg="white").pack(side="left")
            tk.Label(r_frame, text=qty_num, width=10, bg="white", font=("Arial", 10, "bold")).pack(side="left")
            tk.Label(r_frame, text=use, width=30, bg="white", anchor="w", padx=5).pack(side="left")

        # 5. Footer & Chữ ký
        foot = tk.Frame(self.paper, bg="white")
        foot.pack(fill="x", pady=30)
        
        # Lời dặn
        tk.Label(foot, text="* Lời dặn: Tái khám khi hết thuốc hoặc có dấu hiệu bất thường.", font=("Arial", 10, "italic"), bg="white").pack(side="left", anchor="n")
        
        # Chữ ký
        sig_box = tk.Frame(foot, bg="white")
        sig_box.pack(side="right")
        
        try: d, m, y = date.split("-")
        except: d, m, y = "01", "01", "2025"
        
        tk.Label(sig_box, text=f"Hà Nội, ngày {d} tháng {m} năm {y}", font=("Arial", 10, "italic"), bg="white").pack()
        tk.Label(sig_box, text="BÁC SĨ KHÁM BỆNH", font=("Arial", 11, "bold"), bg="white", fg="#b71c1c").pack(pady=5)
        tk.Label(sig_box, text="\n\n\n", bg="white").pack() # Khoảng trống ký
        tk.Label(sig_box, text=doctor.upper(), font=("Arial", 11, "bold"), bg="white").pack()

    def add_line(self, parent, text1, text2, is_bold=False):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=2)
        font = ("Arial", 11, "bold") if is_bold else ("Arial", 11)
        tk.Label(f, text=text1, font=font, bg="white", width=40, anchor="w").pack(side="left")
        tk.Label(f, text=text2, font=font, bg="white", anchor="w").pack(side="left")

    def add_section(self, parent, title, content, highlight=False):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=5)
        tk.Label(f, text=title, font=("Arial", 11, "bold"), bg="white", width=20, anchor="nw").pack(side="left", fill="y")
        
        fg_color = "red" if highlight else "black"
        font_w = "bold" if highlight else "normal"
        
        # Dùng Message để tự xuống dòng nếu text dài
        msg = tk.Message(f, text=content, font=("Arial", 11, font_w), bg="white", fg=fg_color, width=500, anchor="w")
        msg.pack(side="left", fill="x")