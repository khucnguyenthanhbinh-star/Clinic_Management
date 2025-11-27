import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import random
from datetime import datetime

class PatientRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- HEADER ---
        header = tk.Frame(self, bg="white", height=50)
        header.pack(fill="x")
        tk.Label(header, text="QUẢN LÝ HỒ SƠ BỆNH ÁN & ĐIỀU TRỊ", font=("Arial", 16, "bold"), fg="#007bff", bg="white").pack(pady=10, padx=20, anchor="w")

        # --- MAIN LAYOUT (Chia 2 cột) ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # === CỘT TRÁI: DANH SÁCH BỆNH NHÂN ===
        left_frame = ttk.LabelFrame(paned, text="Tìm kiếm bệnh nhân", padding=10)
        paned.add(left_frame, width=350)

        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_patients)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ttk.Label(search_frame, text="🔍").pack(side="right", padx=5)

        # Listbox bệnh nhân
        self.tree_patients = ttk.Treeview(left_frame, columns=("name", "user"), show="headings", selectmode="browse")
        self.tree_patients.heading("name", text="Họ tên")
        self.tree_patients.heading("user", text="Mã BN")
        self.tree_patients.column("name", width=200)
        self.tree_patients.column("user", width=100)
        self.tree_patients.pack(fill="both", expand=True, pady=5)
        
        self.tree_patients.bind("<<TreeviewSelect>>", self.on_select_patient)

        # === CỘT PHẢI: CHI TIẾT HỒ SƠ (TABS) ===
        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame)
        
        # Thông tin hành chính tóm tắt (Sticky Header)
        self.info_header = tk.Frame(self.right_frame, bg="#e3f2fd", pady=10, padx=10)
        self.info_header.pack(fill="x")
        self.lbl_patient_name = tk.Label(self.info_header, text="Vui lòng chọn bệnh nhân", font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0d47a1")
        self.lbl_patient_name.pack(anchor="w")
        self.lbl_patient_details = tk.Label(self.info_header, text="...", font=("Arial", 10), bg="#e3f2fd")
        self.lbl_patient_details.pack(anchor="w")

        # Notebook (Tabs)
        self.tabs = ttk.Notebook(self.right_frame)
        self.tabs.pack(fill="both", expand=True, pady=10)

        # TAB 1: DIỄN TIẾN BỆNH (Lịch sử khám)
        self.setup_tab_history()

        # TAB 2: KẾT QUẢ CẬN LÂM SÀNG (Xét nghiệm/X-Quang)
        self.setup_tab_results()

        # TAB 3: GIẤY TỜ & HÀNH CHÍNH (BHXH, Chuyển viện)
        self.setup_tab_documents()

        # Load dữ liệu ban đầu
        self.load_patient_list()

    # ================== SETUP GIAO DIỆN ==================

    def setup_tab_history(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="📜 Diễn tiến & Lịch sử khám")
        
        # Treeview lịch sử
        cols = ("date", "doc", "diag")
        self.tree_hist = ttk.Treeview(tab, columns=cols, show="headings")
        self.tree_hist.heading("date", text="Ngày khám")
        self.tree_hist.heading("doc", text="Bác sĩ")
        self.tree_hist.heading("diag", text="Chẩn đoán / Diễn tiến")
        self.tree_hist.column("date", width=100)
        self.tree_hist.column("doc", width=150)
        self.tree_hist.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        sb = ttk.Scrollbar(tab, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        # Sự kiện click xem chi tiết đơn thuốc
        self.tree_hist.bind("<Double-1>", self.show_history_detail)

    def setup_tab_results(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="🔬 Kết quả Cận lâm sàng")
        
        # Bảng kết quả
        cols = ("date", "type", "result", "status")
        self.tree_res = ttk.Treeview(tab, columns=cols, show="headings")
        self.tree_res.heading("date", text="Ngày chỉ định")
        self.tree_res.heading("type", text="Loại xét nghiệm/CĐHA")
        self.tree_res.heading("result", text="Kết luận")
        self.tree_res.heading("status", text="Trạng thái")
        
        self.tree_res.column("date", width=100)
        self.tree_res.column("type", width=200)
        self.tree_res.column("result", width=300)
        self.tree_res.column("status", width=100)
        
        self.tree_res.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tag màu
        self.tree_res.tag_configure("done", foreground="green")
        self.tree_res.tag_configure("pending", foreground="orange")

    def setup_tab_documents(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="🖨️ Giấy tờ & Hành chính")
        
        # Các nút chức năng
        lbl = ttk.Label(tab, text="Cấp giấy tờ cho bệnh nhân:", font=("Arial", 12, "bold"))
        lbl.pack(anchor="w", pady=(0, 20))
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=5)
        
        # Nút 1: Giấy nghỉ ốm BHXH
        b1 = tk.Button(btn_frame, text="Giấy nghỉ hưởng BHXH", bg="#4caf50", fg="white", font=("Arial", 10, "bold"), height=2, width=25,
                       command=lambda: self.create_document("bhxh"))
        b1.grid(row=0, column=0, padx=10, pady=10)
        
        # Nút 2: Giấy chuyển tuyến
        b2 = tk.Button(btn_frame, text="Giấy chuyển viện", bg="#ff9800", fg="white", font=("Arial", 10, "bold"), height=2, width=25,
                       command=lambda: self.create_document("transfer"))
        b2.grid(row=0, column=1, padx=10, pady=10)
        
        # Nút 3: Giấy chứng nhận sức khỏe
        b3 = tk.Button(btn_frame, text="Giấy chứng nhận SK", bg="#2196f3", fg="white", font=("Arial", 10, "bold"), height=2, width=25,
                       command=lambda: self.create_document("health"))
        b3.grid(row=1, column=0, padx=10, pady=10)

        # Khu vực hiển thị lịch sử cấp giấy
        ttk.Label(tab, text="Lịch sử cấp giấy tờ:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(30, 5))
        self.txt_doc_log = tk.Text(tab, height=8, state="disabled", bg="#f0f0f0")
        self.txt_doc_log.pack(fill="x")

    # ================== LOGIC XỬ LÝ ==================

    def load_patient_list(self):
        patients = self.controller.db.get_users_by_role("patient")
        self.all_patients = patients # Cache
        self.filter_patients()

    def filter_patients(self, *args):
        keyword = self.search_var.get().lower()
        self.tree_patients.delete(*self.tree_patients.get_children())
        
        for p in self.all_patients:
            if keyword in p['name'].lower() or keyword in p['username'].lower():
                self.tree_patients.insert("", "end", values=(p['name'], p['username']))

    def on_select_patient(self, event):
        sel = self.tree_patients.selection()
        if not sel: return
        
        username = self.tree_patients.item(sel[0])['values'][1]
        user = self.controller.db.get_user(username)
        self.current_patient = user
        
        # 1. Update Header Info
        try:
            info = json.loads(user['info'])
            details = f"NS: {info.get('dob','?')} | GT: {info.get('gender','?')} | SĐT: {info.get('phone','?')}"
            if info.get('history'): details += f"\n⚠️ Tiền sử: {info.get('history')}"
        except: details = "Thông tin chưa cập nhật"
            
        self.lbl_patient_name.config(text=f"{user['name'].upper()} ({username})")
        self.lbl_patient_details.config(text=details)
        
        # 2. Load History
        self.load_history_tab(username)
        
        # 3. Load Lab Results (Giả lập)
        self.load_results_tab(username)
        
        # 4. Clear Document Log
        self.txt_doc_log.config(state="normal"); self.txt_doc_log.delete('1.0', 'end'); self.txt_doc_log.config(state="disabled")

    def load_history_tab(self, username):
        self.tree_hist.delete(*self.tree_hist.get_children())
        apts = self.controller.db.get_appointments(username)
        
        for apt in apts:
            if apt['status'] in ['Hoan thanh', 'Paid']:
                # Parse info
                reason = apt['reason']
                doc_name = "BS Khám"
                diag = reason
                # Logic tách chuỗi cơ bản
                if "CHẨN ĐOÁN:" in reason: # Nếu là format mới của bác sĩ
                    lines = reason.split("\n")
                    for l in lines:
                        if "[" in l and "]" in l: doc_name = l
                        if "CHẨN ĐOÁN:" in l: diag = l.replace("CHẨN ĐOÁN:", "").strip()
                
                self.tree_hist.insert("", "end", values=(apt['date'], doc_name, diag), tags=(reason,))

    def show_history_detail(self, event):
        item = self.tree_hist.selection()
        if not item: return
        full_text = self.tree_hist.item(item[0], "tags")[0]
        
        # Show popup
        top = tk.Toplevel(self)
        top.title("Chi tiết lần khám")
        top.geometry("500x400")
        
        txt = tk.Text(top, padx=10, pady=10, font=("Arial", 10))
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", full_text)
        txt.config(state="disabled")

    def load_results_tab(self, username):
        """
        Hàm này giả lập việc lấy kết quả từ phòng xét nghiệm (LIS/PACS).
        Logic: Quét lịch sử khám, nếu trong nội dung khám có từ khóa 'CHỈ ĐỊNH: X, Y, Z'
        thì sẽ tạo ra các dòng kết quả tương ứng.
        """
        self.tree_res.delete(*self.tree_res.get_children())
        apts = self.controller.db.get_appointments(username)
        
        mock_results_db = {
            "Công thức máu": "Hồng cầu: 4.5T/L (BT), Bạch cầu: 12G/L (Tăng nhẹ)",
            "Sinh hóa máu": "Glucose: 5.5 mmol/L, Creatinin: 90 umol/L",
            "X-Quang": "Tim phổi bình thường, không thấy tổn thương nhu mô.",
            "Siêu âm": "Gan nhiễm mỡ độ 1, Thận trái không sỏi.",
            "Điện tâm đồ": "Nhịp xoang, tần số 80ck/p, trục trung gian."
        }

        for apt in apts:
            if "CHỈ ĐỊNH:" in apt['reason']:
                # Tìm dòng chỉ định
                lines = apt['reason'].split("\n")
                for line in lines:
                    if "CHỈ ĐỊNH:" in line:
                        labs_str = line.replace("CHỈ ĐỊNH:", "").strip()
                        if not labs_str: continue
                        
                        labs = labs_str.split(",")
                        for lab in labs:
                            lab = lab.strip()
                            # Tìm kết quả giả lập
                            res_text = "Đang chờ kết quả..."
                            status = "pending"
                            
                            # Logic giả: Nếu ngày khám < hôm nay -> Có kết quả
                            if apt['date'] < datetime.now().strftime("%Y-%m-%d"):
                                status = "done"
                                # Match từ khóa để lấy kết quả giả
                                for key, val in mock_results_db.items():
                                    if key in lab:
                                        res_text = val
                                        break
                                if res_text == "Đang chờ kết quả...": res_text = "Chỉ số trong giới hạn bình thường."

                            self.tree_res.insert("", "end", values=(apt['date'], lab, res_text, status), tags=(status,))

    def create_document(self, doc_type):
        if not hasattr(self, 'current_patient'):
            messagebox.showwarning("Lỗi", "Vui lòng chọn bệnh nhân trước!")
            return

        p_name = self.current_patient['name'].upper()
        today = datetime.now().strftime("%d/%m/%Y")
        
        content = ""
        title = ""
        
        if doc_type == "bhxh":
            days = simpledialog.askinteger("BHXH", "Số ngày nghỉ:")
            if not days: return
            title = "GIẤY NGHỈ HƯỞNG BẢO HIỂM XÃ HỘI"
            content = (f"Chẩn đoán: Sốt siêu vi (J00)\n"
                       f"Số ngày nghỉ: {days} ngày (Từ {today})\n"
                       f"Đơn vị công tác: Theo khai báo của bệnh nhân.")
                       
        elif doc_type == "transfer":
            hospital = simpledialog.askstring("Chuyển viện", "Tên bệnh viện chuyển đến:")
            if not hospital: return
            title = "GIẤY CHUYỂN TUYẾN"
            content = (f"Chẩn đoán: Viêm phổi nghi lao (J18)\n"
                       f"Lý do chuyển: Vượt quá khả năng chuyên môn.\n"
                       f"Nơi đến: {hospital}")
        
        elif doc_type == "health":
            title = "GIẤY CHỨNG NHẬN SỨC KHỎE"
            content = "Tình trạng sức khỏe: Loại I\nĐủ sức khỏe để học tập và làm việc."

        # Show Preview (Giả lập in)
        msg = f"--- {title} ---\n\n" \
              f"Họ tên: {p_name}\n" \
              f"Ngày cấp: {today}\n\n" \
              f"{content}\n\n" \
              f"[Đã ký bởi Bác sĩ]"
              
        messagebox.showinfo("In ấn thành công", msg)
        
        # Log lại
        self.txt_doc_log.config(state="normal")
        self.txt_doc_log.insert("end", f"[{today}] Đã cấp {title} - {self.controller.auth.current_user}\n")
        self.txt_doc_log.config(state="disabled")