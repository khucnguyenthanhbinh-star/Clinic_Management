import tkinter as tk
from tkinter import ttk
import random
import json

class MedicalRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Layout chính
        self.paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- KHUNG TRÁI: DANH SÁCH ---
        left_frame = ttk.LabelFrame(self.paned, text="Lịch sử khám bệnh", padding=10)
        self.paned.add(left_frame, width=400)

        columns = ("date", "doctor", "diagnosis")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("date", text="Ngày khám")
        self.tree.heading("doctor", text="Bác sĩ")
        self.tree.heading("diagnosis", text="Chẩn đoán")
        
        self.tree.column("date", width=90)
        self.tree.column("doctor", width=120)
        self.tree.column("diagnosis", width=150)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        # --- KHUNG PHẢI: CHI TIẾT (TỜ GIẤY) ---
        self.right_frame = ttk.Frame(self.paned, style="White.TFrame")
        self.paned.add(self.right_frame)

        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("Header.TLabel", background="white", font=("Arial", 14, "bold"), foreground="#003366")
        style.configure("Normal.TLabel", background="white", font=("Arial", 10))
        style.configure("Bold.TLabel", background="white", font=("Arial", 10, "bold"))
        
        self.detail_content = tk.Canvas(self.right_frame, bg="white", highlightthickness=0)
        self.detail_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.detail_content.yview)
        
        self.paper = tk.Frame(self.detail_content, bg="white", padx=40, pady=40)
        
        self.paper.bind("<Configure>", lambda e: self.detail_content.configure(scrollregion=self.detail_content.bbox("all")))
        self.detail_content.create_window((0, 0), window=self.paper, anchor="nw", width=750) # Tăng độ rộng
        self.detail_content.configure(yscrollcommand=self.detail_scrollbar.set)
        
        self.detail_content.pack(side="left", fill="both", expand=True)
        self.detail_scrollbar.pack(side="right", fill="y")

        self.load_history()

    def load_history(self):
        appointments = self.controller.db.get_appointments(self.controller.auth.current_user)
        history_list = [apt for apt in appointments if apt['status'] in ['Hoan thanh', 'Paid']]
        history_list.sort(key=lambda x: x['date'], reverse=True)
        
        for apt in history_list:
            raw_reason = apt['reason']
            doc_name = "Bác sĩ khám"
            diagnosis = raw_reason
            
            if "]" in raw_reason:
                parts = raw_reason.split("]")
                for p in parts:
                    if "BS" in p: doc_name = p.replace("[", "").strip()
                    elif "BOOK" not in p and "BN" not in p and "[" not in p: diagnosis = p.strip()
            
            self.tree.insert("", "end", values=(apt['date'], doc_name, diagnosis), tags=(raw_reason, doc_name))

    def on_select_record(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        date, doctor, diagnosis = item['values']
        self.render_medical_report(date, doctor, diagnosis)

    def render_medical_report(self, date, doctor, diagnosis):
        for widget in self.paper.winfo_children(): widget.destroy()

        # Mock Data
        bp = f"{random.randint(110, 130)}/{random.randint(70, 85)}"
        pulse = str(random.randint(70, 90))
        temp = "36.5"
        weight = str(random.randint(50, 75))

        prescription = []
        advise = ""
        
        if "Nhi" in doctor or "Lien" in doctor:
            prescription = [("Siro ho Prospan", "1 Chai", "Uống 5ml mỗi sáng"), ("Hapacol 150mg", "10 Gói", "Sốt > 38.5 độ uống 1 gói"), ("Oresol", "5 Gói", "Pha uống thay nước")]
            advise = "Theo dõi thân nhiệt, tái khám nếu sốt cao."
        elif "Tim" in doctor or "Hung" in doctor:
            prescription = [("Amlodipine 5mg", "30 Viên", "1 viên sau ăn sáng"), ("Aspirin 81mg", "30 Viên", "1 viên sau ăn trưa"), ("Panangin", "60 Viên", "Sáng 1, Chiều 1")]
            advise = "Hạn chế ăn mặn, tập thể dục nhẹ nhàng."
        elif "Da" in doctor or "Minh" in doctor:
            prescription = [("Fucidin Cream", "1 Tuýp", "Bôi 2 lần/ngày"), ("Vitamin C 500mg", "20 Viên", "1 viên sau ăn"), ("Loratadin 10mg", "10 Viên", "Uống khi ngứa")]
            advise = "Tránh tiếp xúc hóa chất, giữ da khô thoáng."
        else:
            prescription = [("Paracetamol 500mg", "10 Viên", "Uống khi đau"), ("Vitamin tổng hợp", "1 Lọ", "1 viên mỗi sáng"), ("Berberin", "20 Viên", "Uống khi đau bụng")]
            advise = "Ăn uống điều độ, nghỉ ngơi hợp lý."

        # --- GIAO DIỆN PHIẾU KHÁM (ĐÃ SỬA TÊN) ---
        
        # SỬA TẠI ĐÂY: Tên phòng khám chung chung
        ttk.Label(self.paper, text="PHÒNG KHÁM ĐA KHOA QUỐC TẾ", style="Header.TLabel", font=("Arial", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(self.paper, text="Địa chỉ: 123 Đường Giải Phóng, TP. Hà Nội | Hotline: 1900 1234", style="Normal.TLabel").pack()
        
        ttk.Separator(self.paper, orient="horizontal").pack(fill="x", pady=15)
        
        ttk.Label(self.paper, text="PHIẾU KẾT QUẢ KHÁM BỆNH", style="Header.TLabel", font=("Arial", 20, "bold"), foreground="#cc0000").pack(pady=10)
        
        info_frame = tk.Frame(self.paper, bg="white")
        info_frame.pack(fill="x", pady=10)
        
        user_info = self.controller.db.get_user(self.controller.auth.current_user)
        patient_name = user_info['name']
        
        self.row_info(info_frame, "Họ tên bệnh nhân:", patient_name.upper())
        self.row_info(info_frame, "Ngày khám:", date)
        self.row_info(info_frame, "Bác sĩ điều trị:", doctor)
        
        vital_frame = tk.LabelFrame(self.paper, text="Chỉ số sinh tồn", bg="white", font=("Arial", 10, "bold"))
        vital_frame.pack(fill="x", pady=15, ipady=5)
        
        vf = tk.Frame(vital_frame, bg="white"); vf.pack(fill="x", padx=10)
        ttk.Label(vf, text=f"Mạch: {pulse} l/p", style="Normal.TLabel", width=20).pack(side="left")
        ttk.Label(vf, text=f"Huyết áp: {bp} mmHg", style="Normal.TLabel", width=25).pack(side="left")
        ttk.Label(vf, text=f"Nhiệt độ: {temp} °C", style="Normal.TLabel", width=20).pack(side="left")
        ttk.Label(vf, text=f"Cân nặng: {weight} kg", style="Normal.TLabel").pack(side="left")

        ttk.Label(self.paper, text="I. CHẨN ĐOÁN & LÂM SÀNG:", style="Bold.TLabel").pack(anchor="w", pady=(10, 5))
        tk.Label(self.paper, text=f"- Triệu chứng: {diagnosis}\n- Kết luận: Theo dõi và điều trị theo đơn.", 
                 bg="#f0f0f0", fg="black", justify="left", anchor="w", padx=10, pady=10, font=("Arial", 11)).pack(fill="x")

        ttk.Label(self.paper, text="II. CHỈ ĐỊNH ĐIỀU TRỊ & ĐƠN THUỐC:", style="Bold.TLabel").pack(anchor="w", pady=(20, 5))
        
        med_frame = tk.Frame(self.paper, bg="white", highlightbackground="#999", highlightthickness=1)
        med_frame.pack(fill="x")
        
        headers = ["STT", "Tên thuốc / Hàm lượng", "Số lượng", "Cách dùng"]
        widths = [5, 35, 10, 30]
        for col, (txt, w) in enumerate(zip(headers, widths)):
            tk.Label(med_frame, text=txt, bg="#e0e0e0", width=w, relief="solid", borderwidth=1, font=("Arial", 9, "bold")).grid(row=0, column=col, sticky="nsew")
        
        for i, (name, qty, use) in enumerate(prescription, 1):
            tk.Label(med_frame, text=str(i), bg="white", relief="solid", borderwidth=1).grid(row=i, column=0, sticky="nsew")
            tk.Label(med_frame, text=name, bg="white", anchor="w", padx=5, relief="solid", borderwidth=1).grid(row=i, column=1, sticky="nsew")
            tk.Label(med_frame, text=qty, bg="white", relief="solid", borderwidth=1).grid(row=i, column=2, sticky="nsew")
            tk.Label(med_frame, text=use, bg="white", anchor="w", padx=5, relief="solid", borderwidth=1).grid(row=i, column=3, sticky="nsew")

        ttk.Label(self.paper, text="III. LỜI DẶN CỦA BÁC SĨ:", style="Bold.TLabel").pack(anchor="w", pady=(20, 5))
        tk.Label(self.paper, text=advise, bg="white", font=("Arial", 11, "italic"), fg="blue").pack(anchor="w", padx=20)

        sig_frame = tk.Frame(self.paper, bg="white")
        sig_frame.pack(fill="x", pady=40)
        
        try:
            d, m, y = date.split('-')
            date_str = f"Ngày {d} tháng {m} năm {y}"
        except: date_str = date
            
        tk.Label(sig_frame, text=f"Hà Nội, {date_str}", bg="white", font=("Arial", 10, "italic")).pack(side="right", padx=20)
        tk.Label(sig_frame, text="\n\nBÁC SĨ ĐIỀU TRỊ\n\n\n\n", bg="white").pack(side="right")
        tk.Label(sig_frame, text=doctor.upper(), bg="white", font=("Arial", 10, "bold")).place(relx=0.75, rely=0.8)

    def row_info(self, parent, label, value):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, bg="white", font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")
        tk.Label(f, text=value, bg="white", font=("Arial", 10, "bold" if "Họ tên" in label else "normal"), anchor="w").pack(side="left")