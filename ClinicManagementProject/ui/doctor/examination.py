import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

class ExaminationView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_doctor = self.controller.auth.current_user # Username bác sĩ
        
        self.prescription_list = [] 
        self.current_patient_data = None 
        self.current_apt_id = None       
        
        self.medicines_db = self.controller.db.get_medicines()
        self.services_db = dict(self.controller.db.get_services())

        # HEADER
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="TIẾP NHẬN & KHÁM BỆNH", fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # KHUNG GỌI SỐ
        select_frame = ttk.Frame(self)
        select_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(select_frame, text="Gọi bệnh nhân (Của tôi):").pack(side="left")
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(select_frame, textvariable=self.patient_var, width=40, state="readonly")
        self.patient_combo.pack(side="left", padx=10)
        self.patient_combo.bind("<<ComboboxSelected>>", self.load_patient_info)
        
        ttk.Button(select_frame, text="🔄 Tải lại DS", command=self.load_waiting_list).pack(side="left")

        # THÔNG TIN
        info_frame = ttk.LabelFrame(self, text="Thông tin hành chính", padding=10)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        self.lbl_info = ttk.Label(info_frame, text="---", foreground="gray")
        self.lbl_info.pack(side="left", fill="x", expand=True)
        self.lbl_history = ttk.Label(info_frame, text="", foreground="red")
        self.lbl_history.pack(side="right")

        # TABS
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)

        self.setup_tab_diagnosis() 
        self.setup_tab_labs()      
        self.setup_tab_prescription()

        # FOOTER
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        ttk.Button(btn_frame, text="💾 LƯU HỒ SƠ", command=self.finish_examination).pack(side="right", ipadx=20, ipady=5)

        self.load_waiting_list()

    def setup_tab_diagnosis(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="1. Khám & Chẩn đoán")
        
        ttk.Label(tab, text="Lý do / Bệnh sử:").pack(anchor="w")
        self.txt_history = tk.Text(tab, height=2, width=100); self.txt_history.pack(fill="x")
        
        ttk.Label(tab, text="Khám lâm sàng:").pack(anchor="w", pady=(5,0))
        self.txt_exam = tk.Text(tab, height=2, width=100); self.txt_exam.pack(fill="x")
        
        f_diag = ttk.Frame(tab); f_diag.pack(fill="x", pady=5)
        ttk.Label(f_diag, text="Mã ICD-10:").pack(side="left")
        self.cb_icd = ttk.Combobox(f_diag, values=["J00 - Viêm mũi họng", "I10 - Tăng huyết áp", "K29 - Viêm dạ dày"], width=30)
        self.cb_icd.pack(side="left", padx=10)
        
        ttk.Label(tab, text="Chẩn đoán xác định:").pack(anchor="w")
        self.txt_diagnosis = tk.Text(tab, height=2, width=100); self.txt_diagnosis.pack(fill="x")
        
        ttk.Label(tab, text="Lời dặn:").pack(anchor="w", pady=(5,0))
        self.txt_advice = tk.Text(tab, height=2, width=100); self.txt_advice.pack(fill="x")

    def setup_tab_labs(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="2. Cận lâm sàng")
        ttk.Label(tab, text="Chỉ định dịch vụ:").pack(anchor="w", pady=5)
        self.lab_vars = {}
        self.lab_prices = {"Công thức máu": 100000, "Sinh hóa máu": 150000, "X-Quang": 200000, "Siêu âm": 250000, "Điện tâm đồ": 150000, "Nội soi": 500000}
        f_labs = ttk.Frame(tab); f_labs.pack(fill="both", expand=True)
        for i, (lab, price) in enumerate(self.lab_prices.items()):
            var = tk.BooleanVar()
            self.lab_vars[lab] = var
            ttk.Checkbutton(f_labs, text=f"{lab} ({price:,.0f}đ)", variable=var, command=self.refresh_total).grid(row=i//3, column=i%3, sticky="w", padx=20, pady=5)

    def setup_tab_prescription(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="3. Đơn thuốc")
        
        f_input = ttk.LabelFrame(tab, text="Kê đơn", padding=5)
        f_input.pack(fill="x")
        
        ttk.Label(f_input, text="Thuốc:").pack(side="left", padx=5)
        self.cb_med = ttk.Combobox(f_input, values=list(self.medicines_db.keys()), width=25)
        self.cb_med.pack(side="left", padx=5)
        self.cb_med.bind("<<ComboboxSelected>>", self.on_med_select)
        
        self.lbl_stock = ttk.Label(f_input, text="(Tồn: -)")
        self.lbl_stock.pack(side="left", padx=5)
        
        ttk.Label(f_input, text="Số lượng:").pack(side="left", padx=5)
        self.e_qty = ttk.Entry(f_input, width=10); self.e_qty.pack(side="left", padx=5)
        
        ttk.Button(f_input, text="Thêm", command=self.add_medicine).pack(side="left", padx=10)
        
        cols = ("name", "qty", "price", "total")
        self.tree_med = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        self.tree_med.heading("name", text="Tên thuốc"); self.tree_med.column("name", width=250)
        self.tree_med.heading("qty", text="SL"); self.tree_med.column("qty", width=50, anchor="center")
        self.tree_med.heading("price", text="Đơn giá"); self.tree_med.column("price", width=100, anchor="e")
        self.tree_med.heading("total", text="Thành tiền"); self.tree_med.column("total", width=100, anchor="e")
        self.tree_med.pack(fill="both", expand=True, pady=10)
        
        self.lbl_total_bill = ttk.Label(tab, text="Tổng viện phí: 0 VNĐ", foreground="red")
        self.lbl_total_bill.pack(side="right")
        ttk.Button(tab, text="Xóa thuốc chọn", command=self.remove_medicine).pack(side="left")

    def load_waiting_list(self):
        apts = self.controller.db.get_appointments()
        today = datetime.now().strftime("%Y-%m-%d")
        values = []
        self.map_apt = {}
        
        for apt in apts:
            is_my_patient = False
            if apt.get('doctor_username') == self.current_doctor:
                is_my_patient = True
                
            # Điều kiện: Đúng ngày, Trạng thái chờ, Đúng bác sĩ
            if apt['date'] == today and apt['status'] in ["Checked-in", "Da dat", "Unpaid", "Đã đặt"] and is_my_patient:
                u = self.controller.db.get_user(apt['patient'])
                name = u['name'] if u else apt['patient']
                display = f"{apt['time']} - {name} ({apt['status']})"
                values.append(display)
                self.map_apt[display] = apt
                
        self.patient_combo['values'] = values
        if values: self.patient_combo.current(0); self.load_patient_info(None)
        else:
            self.patient_combo.set("")
            self.lbl_info.config(text="Không có bệnh nhân nào đang chờ.")

    def load_patient_info(self, event):
        sel = self.patient_combo.get()
        if not sel: return
        apt = self.map_apt[sel]
        self.current_apt_id = apt['id']
        user = self.controller.db.get_user(apt['patient'])
        self.current_patient_data = user
        
        self.prescription_list = []
        self.refresh_total()
        self.txt_history.delete('1.0', 'end'); 
        # Lấy lý do sạch từ text cũ
        reason = apt['reason']
        if "]" in reason: reason = reason.split("]")[-1].strip()
        self.txt_history.insert('1.0', reason)
        
        self.txt_exam.delete('1.0', 'end'); self.txt_diagnosis.delete('1.0', 'end'); self.txt_advice.delete('1.0', 'end')
        
        try: i = json.loads(user['info'])
        except: i = {}
        self.lbl_info.config(text=f"Bệnh nhân: {user['name']} - {i.get('gender','?')} - {i.get('dob','?')}")
        self.lbl_history.config(text=f"⚠️ {i.get('history','')}" if i.get('history') else "")

    def on_med_select(self, event):
        name = self.cb_med.get()
        if name in self.medicines_db:
            stock = self.medicines_db[name]['quantity']
            price = self.medicines_db[name]['price']
            self.lbl_stock.config(text=f"(Tồn: {stock} | {price:,.0f}đ)")

    def add_medicine(self):
        name = self.cb_med.get()
        qty = self.e_qty.get()
        if name in self.medicines_db and qty.isdigit():
            qty = int(qty)
            stock = self.medicines_db[name]['quantity']
            if qty > stock: return messagebox.showerror("Hết hàng", f"Kho chỉ còn {stock} viên!")
            price = self.medicines_db[name]['price']
            total = qty * price
            self.prescription_list.append({"name": name, "qty": qty, "price": price, "total": total})
            self.medicines_db[name]['quantity'] -= qty 
            self.on_med_select(None); self.refresh_total(); self.e_qty.delete(0, 'end')

    def remove_medicine(self):
        sel = self.tree_med.selection()
        if sel:
            idx = self.tree_med.index(sel[0])
            item = self.prescription_list.pop(idx)
            self.medicines_db[item['name']]['quantity'] += item['qty']
            self.refresh_total()

    def refresh_total(self):
        for i in self.tree_med.get_children(): self.tree_med.delete(i)
        med_total = 0
        for m in self.prescription_list:
            med_total += m['total']
            self.tree_med.insert("", "end", values=(m['name'], m['qty'], f"{m['price']:,.0f}", f"{m['total']:,.0f}"))
        lab_total = sum([self.lab_prices[k] for k, v in self.lab_vars.items() if v.get()])
        grand_total = med_total + lab_total
        self.lbl_total_bill.config(text=f"Tổng viện phí: {grand_total:,.0f} VNĐ")

    def finish_examination(self):
        if not self.current_apt_id: return
        labs = [k for k, v in self.lab_vars.items() if v.get()]
        meds_text = " | ".join([f"{m['name']} ({m['qty']})" for m in self.prescription_list])
        doc_name = self.controller.db.get_user(self.controller.auth.current_user)['name']
        
        report = (f"[{doc_name}]\n"
                  f"CHẨN ĐOÁN: {self.cb_icd.get()} - {self.txt_diagnosis.get('1.0', 'end-1c')}\n"
                  f"CHỈ ĐỊNH: {', '.join(labs)}\n"
                  f"ĐƠN THUỐC: {meds_text}\n"
                  f"LỜI DẶN: {self.txt_advice.get('1.0', 'end-1c')}")
        self.controller.db.finish_examination(self.current_apt_id, report)

        for m in self.prescription_list:
            curr = self.controller.db.cursor.execute("SELECT quantity FROM medicines WHERE name=?", (m['name'],)).fetchone()[0]
            self.controller.db.cursor.execute("UPDATE medicines SET quantity=? WHERE name=?", (curr - m['qty'], m['name']))
        self.controller.db.conn.commit()

        total = sum(m['total'] for m in self.prescription_list) + sum([self.lab_prices[k] for k, v in self.lab_vars.items() if v.get()])
        if total > 0:
            self.controller.db.add_invoice(self.current_patient_data['username'], f"Dịch vụ khám & Thuốc (BS {doc_name})", total, "Unpaid")

        messagebox.showinfo("Thành công", "Đã lưu hồ sơ và tạo hóa đơn!")
        self.load_waiting_list()