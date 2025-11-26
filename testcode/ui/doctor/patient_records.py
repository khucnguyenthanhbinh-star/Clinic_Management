import tkinter as tk
from tkinter import ttk, messagebox

class PatientRecordsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Tiêu đề
        ttk.Label(self, text="HỒ SƠ BỆNH NHÂN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # --- KHUNG TÌM KIẾM ---
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=10)
        
        ttk.Label(search_frame, text="Chọn bệnh nhân:").pack(side="left", padx=5)
        
        # Biến lưu trữ mapping: "Tên hiển thị" -> "username"
        self.patient_map = {}
        self.search_var = tk.StringVar()
        
        self.search_combo = ttk.Combobox(search_frame, textvariable=self.search_var, width=40)
        self.search_combo.pack(side="left", padx=5)
        self.search_combo.bind("<<ComboboxSelected>>", self.on_patient_select)
        
        # Nút tải lại danh sách
        ttk.Button(search_frame, text="Tải lại DS", command=self.load_patient_list).pack(side="left", padx=5)

        # --- KHUNG THÔNG TIN CHI TIẾT ---
        info_frame = ttk.LabelFrame(self, text="Thông tin cá nhân", padding=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_name = ttk.Label(info_frame, text="Họ tên: ---", font=("Arial", 11, "bold"))
        self.lbl_name.grid(row=0, column=0, sticky="w", pady=5)
        
        self.lbl_user = ttk.Label(info_frame, text="Mã BN (Username): ---")
        self.lbl_user.grid(row=0, column=1, sticky="w", pady=5, padx=30)
        
        self.lbl_info = ttk.Label(info_frame, text="Tiền sử/Ghi chú: ---")
        self.lbl_info.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        # --- DANH SÁCH LỊCH SỬ KHÁM ---
        ttk.Label(self, text="Lịch sử khám & Đặt hẹn:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=("date", "time", "reason", "status"), show="headings")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("reason", text="Lý do khám / Chẩn đoán")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("date", width=100)
        self.tree.column("time", width=80)
        self.tree.column("reason", width=400)
        self.tree.column("status", width=120)
        
        self.tree.pack(fill="both", expand=True)

        # Tải danh sách ngay khi mở màn hình
        self.load_patient_list()

    def load_patient_list(self):
        """Lấy danh sách bệnh nhân từ DB nạp vào Combobox"""
        patients = self.controller.db.get_users_by_role("patient")
        self.patient_map = {}
        display_values = []
        
        for p in patients:
            # Format: "Nguyen Van A (bn1)" để dễ phân biệt
            display_str = f"{p['name']} ({p['username']})"
            self.patient_map[display_str] = p['username']
            display_values.append(display_str)
            
        self.search_combo['values'] = display_values
        if display_values:
            self.search_combo.current(0)
            self.on_patient_select(None) # Tự động load người đầu tiên

    def on_patient_select(self, event):
        """Khi chọn một bệnh nhân, load thông tin và lịch sử"""
        selection = self.search_var.get()
        if not selection or selection not in self.patient_map:
            return
            
        username = self.patient_map[selection]
        
        # 1. Load thông tin cá nhân
        user_info = self.controller.db.get_user(username)
        if user_info:
            self.lbl_name.config(text=f"Họ tên: {user_info['name']}")
            self.lbl_user.config(text=f"Mã BN: {user_info['username']}")
            # Nếu info trống thì ghi là "Không có"
            info_text = user_info['info'] if user_info['info'] else "Không có ghi chú đặc biệt"
            self.lbl_info.config(text=f"Tiền sử/Ghi chú: {info_text}")
        
        # 2. Load lịch sử khám (Appointments)
        # Xóa dữ liệu cũ trên bảng
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Lấy dữ liệu mới từ DB
        history = self.controller.db.get_appointments(username)
        
        # Sắp xếp theo ngày giảm dần (mới nhất lên đầu)
        history.sort(key=lambda x: x['date'], reverse=True)
        
        for apt in history:
            self.tree.insert("", "end", values=(apt["date"], apt["time"], apt["reason"], apt["status"]))