import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import random
from datetime import datetime

class PatientRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_doctor = self.controller.auth.current_user # Username bác sĩ hiện tại
        
        # --- HEADER ---
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="TRA CỨU HỒ SƠ BỆNH NHÂN (CỦA TÔI)", font=("Arial", 16, "bold"), fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # --- MAIN LAYOUT ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # === CỘT TRÁI: DANH SÁCH BỆNH NHÂN ===
        left_frame = ttk.LabelFrame(paned, text="Danh sách bệnh nhân đã/đang khám", padding=10)
        paned.add(left_frame, width=350)

        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_patients)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ttk.Label(search_frame, text="🔍").pack(side="right", padx=5)

        # Listbox
        self.tree_patients = ttk.Treeview(left_frame, columns=("name", "user"), show="headings", selectmode="browse")
        self.tree_patients.heading("name", text="Họ tên")
        self.tree_patients.heading("user", text="Mã BN")
        self.tree_patients.column("name", width=200)
        self.tree_patients.column("user", width=100)
        self.tree_patients.pack(fill="both", expand=True, pady=5)
        
        self.tree_patients.bind("<<TreeviewSelect>>", self.on_select_patient)

        # === CỘT PHẢI: CHI TIẾT HỒ SƠ ===
        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame)
        
        # Header Info
        self.info_header = tk.Frame(self.right_frame, bg="#e3f2fd", pady=10, padx=10)
        self.info_header.pack(fill="x")
        self.lbl_patient_name = tk.Label(self.info_header, text="<Chọn bệnh nhân>", font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0d47a1")
        self.lbl_patient_name.pack(anchor="w")
        self.lbl_patient_details = tk.Label(self.info_header, text="...", font=("Arial", 10), bg="#e3f2fd")
        self.lbl_patient_details.pack(anchor="w")

        # Tabs
        self.tabs = ttk.Notebook(self.right_frame)
        self.tabs.pack(fill="both", expand=True, pady=10)

        self.setup_tab_history()
        self.setup_tab_results()
        self.setup_tab_documents()

        # Load dữ liệu (Logic mới)
        self.load_my_patient_list()

    # ================== LOGIC XỬ LÝ ==================

    def load_my_patient_list(self):
        # 1. Lấy tất cả lịch hẹn
        all_apts = self.controller.db.get_appointments()
        
        # 2. Lọc ra danh sách username bệnh nhân CÓ LIÊN QUAN đến bác sĩ này
        my_patient_usernames = set()
        
        for apt in all_apts:
            # Điều kiện: Lịch hẹn có doctor_username trùng với bác sĩ đang đăng nhập
            if apt.get('doctor_username') == self.current_doctor:
                my_patient_usernames.add(apt['patient'])
        
        # 3. Lấy thông tin chi tiết của các bệnh nhân đó
        self.my_patients = []
        for username in my_patient_usernames:
            user = self.controller.db.get_user(username)
            if user:
                self.my_patients.append(user)
        
        # Hiển thị lên bảng
        self.filter_patients()

    def filter_patients(self, *args):
        keyword = self.search_var.get().lower()
        self.tree_patients.delete(*self.tree_patients.get_children())
        
        for p in self.my_patients:
            if keyword in p['name'].lower() or keyword in p['username'].lower():
                self.tree_patients.insert("", "end", values=(p['name'], p['username']))

    def on_select_patient(self, event):
        sel = self.tree_patients.selection()
        if not sel: return
        
        username = self.tree_patients.item(sel[0])['values'][1]
        user = self.controller.db.get_user(username)
        self.current_patient = user
        
        # Update Header
        try:
            info = json.loads(user['info'])
            details = f"NS: {info.get('dob','?')} | GT: {info.get('gender','?')} | SĐT: {info.get('phone','?')}"
            if info.get('history'): details += f"\n⚠️ Tiền sử: {info.get('history')}"
        except: details = "Thông tin chưa cập nhật"
            
        self.lbl_patient_name.config(text=f"{user['name'].upper()} ({username})")
        self.lbl_patient_details.config(text=details)
        
        # Load Tabs
        self.load_history_tab(username)
        self.load_results_tab(username)
        self.txt_doc_log.config(state="normal"); self.txt_doc_log.delete('1.0', 'end'); self.txt_doc_log.config(state="disabled")

    def setup_tab_history(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="📜 Lịch sử khám bệnh")
        cols = ("date", "doc", "diag")
        self.tree_hist = ttk.Treeview(tab, columns=cols, show="headings")
        self.tree_hist.heading("date", text="Ngày khám")
        self.tree_hist.heading("doc", text="Bác sĩ")
        self.tree_hist.heading("diag", text="Chẩn đoán / Lý do")
        self.tree_hist.column("date", width=100)
        self.tree_hist.column("doc", width=150)
        self.tree_hist.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sb = ttk.Scrollbar(tab, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sb.set); sb.pack(side="right", fill="y")
        self.tree_hist.bind("<Double-1>", self.show_history_detail)

    def load_history_tab(self, username):
        self.tree_hist.delete(*self.tree_hist.get_children())
        apts = self.controller.db.get_appointments(username)
        for apt in apts:
            if apt['status'] in ['Hoan thanh', 'Paid']:
                doc_name = "BS Khám"
                if apt.get('doctor_username'):
                    u = self.controller.db.get_user(apt['doctor_username'])
                    if u: doc_name = u['name']
                
                diag = apt['reason']
                if "CHẨN ĐOÁN:" in diag: diag = diag.split("CHẨN ĐOÁN:")[1].split("\n")[0].strip()
                elif "]" in diag: diag = diag.split("]")[-1].strip()
                
                self.tree_hist.insert("", "end", values=(apt['date'], doc_name, diag), tags=(apt['reason'],))

    def show_history_detail(self, event):
        item = self.tree_hist.selection()
        if not item: return
        full_text = self.tree_hist.item(item[0], "tags")[0]
        top = tk.Toplevel(self); top.title("Chi tiết lần khám"); top.geometry("500x400")
        txt = tk.Text(top, padx=10, pady=10, font=("Arial", 10))
        txt.pack(fill="both", expand=True); txt.insert("1.0", full_text); txt.config(state="disabled")

    def setup_tab_results(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="🔬 Kết quả Cận lâm sàng")
        cols = ("date", "type", "result", "status")
        self.tree_res = ttk.Treeview(tab, columns=cols, show="headings")
        self.tree_res.heading("date", text="Ngày"); self.tree_res.heading("type", text="Loại XN"); self.tree_res.heading("result", text="Kết quả"); self.tree_res.heading("status", text="TT")
        self.tree_res.column("date", width=90); self.tree_res.column("type", width=150); self.tree_res.column("result", width=250); self.tree_res.column("status", width=80)
        self.tree_res.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_res.tag_configure("done", foreground="green"); self.tree_res.tag_configure("pending", foreground="orange")

    def load_results_tab(self, username):
        self.tree_res.delete(*self.tree_res.get_children())
        apts = self.controller.db.get_appointments(username)
        mock_results = {"Công thức máu": "Bạch cầu tăng nhẹ", "Sinh hóa máu": "Bình thường", "X-Quang": "Tim phổi bình thường", "Siêu âm": "Gan nhiễm mỡ độ 1"}
        for apt in apts:
            if "CHỈ ĐỊNH:" in apt['reason']:
                for line in apt['reason'].split("\n"):
                    if "CHỈ ĐỊNH:" in line:
                        labs = line.replace("CHỈ ĐỊNH:", "").strip().split(",")
                        for lab in labs:
                            lab = lab.strip(); res = "Đang chờ..."; st = "pending"
                            if apt['date'] < datetime.now().strftime("%Y-%m-%d"): st = "done"; res = mock_results.get(lab.split("(")[0].strip(), "Bình thường")
                            self.tree_res.insert("", "end", values=(apt['date'], lab, res, st), tags=(st,))

    def setup_tab_documents(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="🖨️ Giấy tờ")
        lbl = ttk.Label(tab, text="Cấp giấy tờ:", font=("Arial", 12, "bold")); lbl.pack(anchor="w", pady=(0, 20))
        btn_frame = ttk.Frame(tab); btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Giấy nghỉ BHXH", bg="#4caf50", fg="white", command=lambda: self.create_document("bhxh")).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Giấy chuyển viện", bg="#ff9800", fg="white", command=lambda: self.create_document("transfer")).grid(row=0, column=1, padx=10)
        ttk.Label(tab, text="Lịch sử cấp:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(30, 5))
        self.txt_doc_log = tk.Text(tab, height=8, state="disabled", bg="#f0f0f0"); self.txt_doc_log.pack(fill="x")

    def create_document(self, doc_type):
        if not hasattr(self, 'current_patient'): return messagebox.showwarning("Lỗi", "Chọn bệnh nhân trước!")
        p_name = self.current_patient['name'].upper(); today = datetime.now().strftime("%d/%m/%Y")
        if doc_type == "bhxh":
            days = simpledialog.askinteger("BHXH", "Số ngày nghỉ:")
            if days: 
                msg = f"--- GIẤY NGHỈ BHXH ---\nHọ tên: {p_name}\nNghỉ: {days} ngày kể từ {today}\nBS chỉ định: {self.controller.auth.current_user}"
                messagebox.showinfo("In thành công", msg)
                self.txt_doc_log.config(state="normal"); self.txt_doc_log.insert("end", f"[{today}] Cấp BHXH ({days} ngày)\n"); self.txt_doc_log.config(state="disabled")
        elif doc_type == "transfer":
            hos = simpledialog.askstring("Chuyển viện", "Đến bệnh viện:")
            if hos:
                msg = f"--- GIẤY CHUYỂN VIỆN ---\nBệnh nhân: {p_name}\nChuyển đến: {hos}\nLý do: Vượt khả năng chuyên môn"
                messagebox.showinfo("In thành công", msg)
                self.txt_doc_log.config(state="normal"); self.txt_doc_log.insert("end", f"[{today}] Chuyển viện -> {hos}\n"); self.txt_doc_log.config(state="disabled")