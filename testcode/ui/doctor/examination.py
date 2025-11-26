import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

class ExaminationView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_patient_data = None 
        self.current_apt_id = None       

        # --- HEADER ---
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="TIẾP NHẬN & KHÁM BỆNH", font=("Arial", 16, "bold"), fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # --- KHUNG CHỌN BỆNH NHÂN ---
        select_frame = ttk.Frame(self)
        select_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(select_frame, text="Gọi bệnh nhân (Đang chờ):", font=("Arial", 11, "bold")).pack(side="left")
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(select_frame, textvariable=self.patient_var, width=40, state="readonly")
        self.patient_combo.pack(side="left", padx=10)
        self.patient_combo.bind("<<ComboboxSelected>>", self.load_patient_info)
        
        ttk.Button(select_frame, text="🔄 Tải lại DS", command=self.load_waiting_list).pack(side="left")

        # --- THÔNG TIN HÀNH CHÍNH ---
        info_frame = ttk.LabelFrame(self, text="Thông tin bệnh nhân & Dấu hiệu sinh tồn", padding=10)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        self.lbl_info = ttk.Label(info_frame, text="Chưa chọn bệnh nhân", font=("Arial", 10, "bold"), foreground="gray")
        self.lbl_info.grid(row=0, column=0, columnspan=4, sticky="w", pady=5)
        
        self.lbl_history = ttk.Label(info_frame, text="", foreground="red")
        self.lbl_history.grid(row=0, column=4, columnspan=2, sticky="e")

        ttk.Label(info_frame, text="Mạch (l/p):").grid(row=1, column=0, sticky="e")
        self.e_pulse = ttk.Entry(info_frame, width=10); self.e_pulse.grid(row=1, column=1, padx=5)
        
        ttk.Label(info_frame, text="Huyết áp (mmHg):").grid(row=1, column=2, sticky="e")
        self.e_bp = ttk.Entry(info_frame, width=10); self.e_bp.grid(row=1, column=3, padx=5)
        
        ttk.Label(info_frame, text="Nhiệt độ (°C):").grid(row=1, column=4, sticky="e")
        self.e_temp = ttk.Entry(info_frame, width=10); self.e_temp.grid(row=1, column=5, padx=5)
        
        ttk.Label(info_frame, text="Cân nặng (kg):").grid(row=1, column=6, sticky="e")
        self.e_weight = ttk.Entry(info_frame, width=10); self.e_weight.grid(row=1, column=7, padx=5)

        # --- TABS (ĐÃ XÓA TAB ĐƠN THUỐC) ---
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)

        self.setup_tab_diagnosis() # Tab 1
        self.setup_tab_labs()      # Tab 2

        # --- FOOTER ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="LƯU & HOÀN TẤT KHÁM", command=self.finish_examination).pack(side="right", ipadx=20, ipady=5)

        self.load_waiting_list()

    def setup_tab_diagnosis(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="1. Khám & Chẩn đoán")
        
        ttk.Label(tab, text="Lý do đến khám / Bệnh sử:").pack(anchor="w")
        self.txt_history = tk.Text(tab, height=3, width=100); self.txt_history.pack(fill="x", pady=5)
        
        ttk.Label(tab, text="Khám lâm sàng:").pack(anchor="w")
        self.txt_exam = tk.Text(tab, height=3, width=100); self.txt_exam.pack(fill="x", pady=5)
        
        f_diag = ttk.Frame(tab)
        f_diag.pack(fill="x", pady=5)
        ttk.Label(f_diag, text="Mã ICD-10:").pack(side="left")
        self.cb_icd = ttk.Combobox(f_diag, values=["J00 - Viêm mũi họng cấp", "J20 - Viêm phế quản cấp", "I10 - Tăng huyết áp", "K29 - Viêm dạ dày", "L20 - Viêm da cơ địa"], width=30)
        self.cb_icd.pack(side="left", padx=10)
        
        ttk.Label(tab, text="Chẩn đoán xác định:").pack(anchor="w")
        self.txt_diagnosis = tk.Text(tab, height=2, width=100); self.txt_diagnosis.pack(fill="x", pady=5)
        
        ttk.Label(tab, text="Lời dặn / Hướng điều trị:").pack(anchor="w")
        self.txt_advice = tk.Text(tab, height=3, width=100); self.txt_advice.pack(fill="x", pady=5)

    def setup_tab_labs(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="2. Cận lâm sàng")
        ttk.Label(tab, text="Chọn chỉ định (Tích chọn):", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        self.lab_vars = {}
        labs = ["Công thức máu (CBC)", "Sinh hóa máu (Gan, Thận)", "Đường huyết (Glucose)", "Tổng phân tích nước tiểu", "X-Quang ngực thẳng", "Siêu âm bụng tổng quát", "Điện tâm đồ (ECG)", "Nội soi Tai Mũi Họng"]
        f_labs = ttk.Frame(tab)
        f_labs.pack(fill="both", expand=True)
        for i, lab in enumerate(labs):
            var = tk.BooleanVar()
            self.lab_vars[lab] = var
            ttk.Checkbutton(f_labs, text=lab, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)

    def load_waiting_list(self):
        apts = self.controller.db.get_appointments()
        today = datetime.now().strftime("%Y-%m-%d")
        values = []
        self.map_apt = {}
        for apt in apts:
            if apt['date'] == today and apt['status'] in ["Checked-in", "Da dat", "Unpaid", "Đã đặt"]:
                user = self.controller.db.get_user(apt['patient'])
                name = user['name'] if user else apt['patient']
                display = f"{apt['time']} - {name} ({apt['status']})"
                values.append(display)
                self.map_apt[display] = apt
        self.patient_combo['values'] = values
        if values: self.patient_combo.current(0); self.load_patient_info(None)

    def load_patient_info(self, event):
        selection = self.patient_combo.get()
        if not selection: return
        apt = self.map_apt[selection]
        self.current_apt_id = apt['id']
        user = self.controller.db.get_user(apt['patient'])
        self.current_patient_data = user
        try:
            info = json.loads(user['info'])
            dob = info.get('dob', 'Unknown'); history = info.get('history', ''); gender = info.get('gender', '')
        except: dob = "??"; history = ""; gender = ""
        self.lbl_info.config(text=f"Bệnh nhân: {user['name']} | Giới tính: {gender} | Ngày sinh: {dob}", foreground="#007bff")
        if history: self.lbl_history.config(text=f"⚠️ TIỀN SỬ: {history}")
        else: self.lbl_history.config(text="")
        self.e_pulse.delete(0, 'end'); self.e_bp.delete(0, 'end'); self.e_temp.delete(0, 'end'); self.e_weight.delete(0, 'end')
        self.txt_history.delete('1.0', 'end'); self.txt_history.insert('1.0', apt['reason'])
        self.txt_exam.delete('1.0', 'end'); self.txt_diagnosis.delete('1.0', 'end'); self.txt_advice.delete('1.0', 'end')

    def finish_examination(self):
        if not self.current_apt_id: return messagebox.showwarning("Lỗi", "Chưa chọn bệnh nhân!")
        
        diagnosis_icd = self.cb_icd.get()
        diagnosis_text = self.txt_diagnosis.get("1.0", "end-1c")
        advice = self.txt_advice.get("1.0", "end-1c")
        labs = [k for k, v in self.lab_vars.items() if v.get()]
        
        # Format không có đơn thuốc
        doctor_name = self.controller.db.get_user(self.controller.auth.current_user)['name']
        
        full_report = (
            f"[{doctor_name}]\n"
            f"CHẨN ĐOÁN: {diagnosis_icd} - {diagnosis_text}\n"
            f"CHỈ ĐỊNH: {', '.join(labs)}\n"
            f"LỜI DẶN: {advice}"
        )
        
        self.controller.db.finish_examination(self.current_apt_id, full_report)
        messagebox.showinfo("Thành công", "Đã lưu kết quả khám.")
        self.load_waiting_list()