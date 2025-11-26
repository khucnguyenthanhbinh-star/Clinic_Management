import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import random

class BookAppointmentView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Dữ liệu đặt lịch
        self.booking_data = {
            "clinic_id": "", "clinic_name": "",     
            "specialty": "", "service": "", "service_price": 0,    
            "doctor_username": "", "doctor_name": "", "doctor_price": 0,
            "date": "", "time": "",
            "patient_name": "", "reason": ""
        }

        # Header
        self.header_lbl = ttk.Label(self, text="LỄ TÂN: ĐĂNG KÝ LỊCH KHÁM", font=("Arial", 16, "bold"), foreground="#d9534f")
        self.header_lbl.pack(pady=10)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=5)

        # Bắt đầu quy trình
        self.show_step_1_clinic()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ================= BƯỚC 1: CHỌN CƠ SỞ =================
    def show_step_1_clinic(self):
        self.clear_container()
        self.header_lbl.config(text="BƯỚC 1: CHỌN CƠ SỞ")
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Chọn cơ sở tiếp nhận:", font=("Arial", 12)).pack(anchor="w", pady=20)

        self.clinics = [("CS1", "Cơ sở 1: 123 Cầu Giấy, Hà Nội"), ("CS2", "Cơ sở 2: 45 Hàng Bài, Hà Nội")]
        self.clinic_var = tk.StringVar(value="CS1")
        for code, name in self.clinics:
            ttk.Radiobutton(frame, text=name, variable=self.clinic_var, value=code).pack(anchor="w", padx=20, pady=5)

        ttk.Button(frame, text="Tiếp tục >>", command=self.save_step_1).pack(pady=30, fill="x", ipady=5)

    def save_step_1(self):
        code = self.clinic_var.get()
        for c, name in self.clinics:
            if c == code: self.booking_data["clinic_name"] = name; break
        self.booking_data["clinic_id"] = code
        self.show_step_2_service()

    # ================= BƯỚC 2: CHỌN DỊCH VỤ =================
    def show_step_2_service(self):
        self.clear_container()
        self.header_lbl.config(text="BƯỚC 2: CHỌN DỊCH VỤ")
        ttk.Button(self.container, text="<< Quay lại", command=self.show_step_1_clinic).pack(anchor="w")
        
        frame = ttk.Frame(self.container); frame.pack(fill="both", expand=True, pady=10)
        
        # Lọc chuyên khoa
        doctors = self.controller.db.get_users_by_role("doctor")
        specialties = set()
        for d in doctors:
            try:
                info = json.loads(d['info'])
                if info.get("branch") == self.booking_data["clinic_id"]: specialties.add(info.get("specialty", "Đa khoa"))
            except: pass
        if not specialties: specialties.add("Đa khoa")

        ttk.Label(frame, text="Chuyên khoa:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.specialty_var = tk.StringVar()
        cb = ttk.Combobox(frame, textvariable=self.specialty_var, values=list(specialties), state="readonly"); cb.pack(fill="x", pady=5); cb.current(0)

        ttk.Label(frame, text="Dịch vụ:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(15,5))
        self.services = [("Khám thường", 0), ("Khám VIP", 200000), ("Cấp cứu", 500000)]
        self.service_var = tk.StringVar(value="Khám thường")
        for name, price in self.services: ttk.Radiobutton(frame, text=name, variable=self.service_var, value=name).pack(anchor="w", padx=10)

        ttk.Button(frame, text="Tiếp tục >>", command=self.save_step_2).pack(pady=30, fill="x", ipady=5)

    def save_step_2(self):
        self.booking_data["specialty"] = self.specialty_var.get()
        self.booking_data["service"] = self.service_var.get()
        for n, p in self.services:
            if n == self.booking_data["service"]: self.booking_data["service_price"] = p; break
        self.show_step_3_doctor()

    # ================= BƯỚC 3: CHỌN BÁC SĨ =================
    def show_step_3_doctor(self):
        self.clear_container()
        self.header_lbl.config(text="BƯỚC 3: CHỌN BÁC SĨ")
        ttk.Button(self.container, text="<< Quay lại", command=self.show_step_2_service).pack(anchor="w")

        # Logic lọc bác sĩ
        all_docs = self.controller.db.get_users_by_role("doctor")
        filtered = []
        for d in all_docs:
            try:
                info = json.loads(d['info'])
                if info.get("specialty") == self.booking_data["specialty"] and info.get("branch") == self.booking_data["clinic_id"]:
                    d['parsed_info'] = info; filtered.append(d)
            except: pass
        
        if not filtered: 
            ttk.Label(self.container, text="Không có bác sĩ phù hợp!").pack(pady=20); return

        canvas = tk.Canvas(self.container); scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, pady=10); scrollbar.pack(side="right", fill="y")

        for doc in filtered:
            info = doc['parsed_info']
            card = ttk.LabelFrame(scroll_frame, text=f" {doc['name']} "); card.pack(fill="x", pady=5, padx=5)
            card.columnconfigure(0, weight=1); card.columnconfigure(1, weight=0)
            
            f_info = ttk.Frame(card); f_info.grid(row=0, column=0, sticky="nsew", padx=10)
            ttk.Label(f_info, text=f"Kinh nghiệm: {info.get('exp')} năm").pack(anchor="w")
            ttk.Label(f_info, text=f"Đánh giá: {info.get('rating')} ⭐", foreground="orange").pack(anchor="w")
            
            f_act = ttk.Frame(card); f_act.grid(row=0, column=1, sticky="e", padx=10)
            ttk.Label(f_act, text=f"{info.get('price'):,.0f} đ", foreground="red", font=("Arial",10,"bold")).pack(anchor="e")
            ttk.Button(f_act, text="CHỌN", command=lambda d=doc: self.save_step_3(d)).pack(pady=5)

    def save_step_3(self, doc):
        self.booking_data["doctor_username"] = doc["username"]
        self.booking_data["doctor_name"] = doc["name"]
        self.booking_data["doctor_price"] = doc["parsed_info"].get("price", 0)
        self.show_step_4_time()

    # ================= BƯỚC 4: CHỌN NGÀY GIỜ =================
    def show_step_4_time(self):
        self.clear_container()
        self.header_lbl.config(text="BƯỚC 4: CHỌN LỊCH")
        ttk.Button(self.container, text="<< Quay lại", command=self.show_step_3_doctor).pack(anchor="w")

        f_date = ttk.Frame(self.container); f_date.pack(pady=10)
        ttk.Label(f_date, text="Ngày:").pack(side="left")
        
        self.date_combo = ttk.Combobox(f_date, state="readonly", width=25)
        self.dates_map = []
        for i in range(0, 8): # Lễ tân có thể đặt ngay hôm nay (i=0)
            d = datetime.now() + timedelta(days=i)
            self.dates_map.append(d.strftime("%Y-%m-%d"))
            self.date_combo['values'] = (*self.date_combo['values'], d.strftime("%d/%m/%Y (%A)"))
        self.date_combo.current(0); self.date_combo.pack(side="left", padx=10)
        self.date_combo.bind("<<ComboboxSelected>>", self.load_slots)

        self.slot_frame = ttk.LabelFrame(self.container, text="Giờ trống", padding=10)
        self.slot_frame.pack(fill="both", expand=True, padx=20)
        self.load_slots(None)

    def load_slots(self, event):
        for w in self.slot_frame.winfo_children(): w.destroy()
        self.booking_data["date"] = self.dates_map[self.date_combo.current()]
        
        booked = [a['time'] for a in self.controller.db.get_appointments() 
                  if a['date'] == self.booking_data["date"] and f"[{self.booking_data['doctor_name']}]" in a['reason']]
        
        times = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
        r, c = 0, 0
        for t in times:
            st = "disabled" if t in booked else "normal"
            txt = f"{t} (Full)" if t in booked else t
            ttk.Button(self.slot_frame, text=txt, state=st, command=lambda x=t: self.save_step_4(x)).grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            c+=1; 
            if c>3: c=0; r+=1

    def save_step_4(self, time):
        self.booking_data["time"] = time
        self.show_step_5_info()

    # ================= BƯỚC 5: THÔNG TIN BỆNH NHÂN (NHẬP TAY) =================
    def show_step_5_info(self):
        self.clear_container()
        self.header_lbl.config(text="BƯỚC 5: THÔNG TIN BỆNH NHÂN")
        ttk.Button(self.container, text="<< Quay lại", command=self.show_step_4_time).pack(anchor="w")

        frame = ttk.LabelFrame(self.container, text="Thông tin bệnh nhân", padding=10)
        frame.pack(fill="x", pady=10)
        
        self.e_name = self.mk_inp(frame, "Họ tên (*):", 0)
        self.e_phone = self.mk_inp(frame, "SĐT (*):", 1)
        self.e_dob = self.mk_inp(frame, "Ngày sinh (*):", 2)
        self.e_cccd = self.mk_inp(frame, "CCCD/CMND (*):", 3)
        
        ttk.Label(frame, text="Giới tính (*):").grid(row=4, column=0, sticky="e", pady=5, padx=5)
        self.cb_gender = ttk.Combobox(frame, values=["Nam", "Nữ"], state="readonly", width=28); self.cb_gender.current(0)
        self.cb_gender.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(self.container, text="Lý do khám:").pack(anchor="w", pady=(10,5))
        self.e_reason = ttk.Entry(self.container, width=50); self.e_reason.pack(fill="x")

        ttk.Button(self.container, text="XÁC NHẬN ĐẶT LỊCH", command=self.save_step_5).pack(pady=20, ipadx=10)

    def mk_inp(self, parent, lbl, r):
        ttk.Label(parent, text=lbl).grid(row=r, column=0, sticky="e", pady=5, padx=5)
        e = ttk.Entry(parent, width=30); e.grid(row=r, column=1, pady=5)
        return e

    def save_step_5(self):
        reason = self.e_reason.get().strip()
        if not reason: return messagebox.showerror("Thiếu thông tin", "Vui lòng nhập lý do khám!")
        self.booking_data["reason"] = reason

        name = self.e_name.get().strip()
        phone = self.e_phone.get().strip()
        dob = self.e_dob.get().strip()
        cccd = self.e_cccd.get().strip()
        
        if not (name and phone and dob and cccd):
            return messagebox.showerror("Thiếu thông tin", "Vui lòng điền ĐẦY ĐỦ thông tin bệnh nhân!")
        
        self.booking_data["patient_name"] = name
        
        # Tự động tạo hóa đơn và lịch hẹn
        self.finish()

    def finish(self):
        total = self.booking_data["doctor_price"] + self.booking_data["service_price"]
        code = f"RC{random.randint(1000,9999)}"
        
        # Lưu với user là người đang đăng nhập (Lễ tân), nhưng ghi chú là đặt cho ai
        reason = f"[{code}] [{self.booking_data['clinic_id']}] [{self.booking_data['doctor_name']}] [BN: {self.booking_data['patient_name']}] {self.booking_data['reason']}"
        
        self.controller.db.add_appointment(self.controller.auth.current_user, self.booking_data['date'], self.booking_data['time'], reason)
        
        # Tạo hóa đơn chưa thanh toán
        self.controller.db.add_invoice(self.controller.auth.current_user, f"Phí khám {code} (BN: {self.booking_data['patient_name']})", total, "Unpaid")
        
        messagebox.showinfo("Thành công", f"Đã đặt lịch thành công!\nMã hồ sơ: {code}")
        self.show_step_1_clinic() # Quay lại từ đầu để đặt tiếp