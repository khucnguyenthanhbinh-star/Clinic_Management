import tkinter as tk
from tkinter import ttk, messagebox
import json

class UpdateInfoView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_username = self.controller.auth.current_user
        
        ttk.Label(self, text="HỒ SƠ BỆNH ÁN ĐIỆN TỬ", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Canvas cuộn
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load dữ liệu
        user_row = self.controller.db.get_user(self.current_username)
        self.current_name = user_row['name']
        raw_info = user_row['info']
        self.data = {}
        try:
            self.data = json.loads(raw_info) if raw_info else {}
        except:
            self.data = {}

        # --- FORM NHẬP LIỆU ---
        
        # Nhóm thông tin BẮT BUỘC
        group_req = ttk.LabelFrame(self.scrollable_frame, text="Thông tin bắt buộc (*)", padding=15)
        group_req.pack(fill="x", padx=20, pady=10)

        # Họ tên
        self.create_row(group_req, 0, "Họ và tên (*):", self.current_name, "name")
        # Số điện thoại
        self.create_row(group_req, 1, "Số điện thoại (*):", self.data.get("phone", ""), "phone")
        # CCCD
        self.create_row(group_req, 2, "Số CCCD/CMND (*):", self.data.get("cccd", ""), "cccd")
        # Ngày sinh
        self.create_row(group_req, 3, "Ngày sinh (dd/mm/yyyy) (*):", self.data.get("dob", ""), "dob")
        
        # Giới tính (Combobox)
        ttk.Label(group_req, text="Giới tính (*):", foreground="red").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.combo_gender = ttk.Combobox(group_req, values=["Nam", "Nữ", "Khác"], width=27, state="readonly")
        self.combo_gender.set(self.data.get("gender", "Nam"))
        self.combo_gender.grid(row=4, column=1, padx=5, pady=5)

        # Nhóm thông tin BỔ SUNG
        group_opt = ttk.LabelFrame(self.scrollable_frame, text="Thông tin bổ sung", padding=15)
        group_opt.pack(fill="x", padx=20, pady=10)

        self.create_row(group_opt, 0, "Địa chỉ:", self.data.get("address", ""), "address")
        self.create_row(group_opt, 1, "Mã BHYT:", self.data.get("insurance", ""), "insurance")
        self.create_row(group_opt, 2, "Tiền sử bệnh:", self.data.get("history", ""), "history")

        # Nút Lưu
        ttk.Button(self.scrollable_frame, text="Lưu hồ sơ", command=self.save_data).pack(pady=20, ipadx=20)

        # Lưu tham chiếu các entry để lấy dữ liệu sau
        self.entries = {}

    def create_row(self, parent, row, label_text, value, key):
        """Hàm hỗ trợ tạo dòng nhập liệu nhanh"""
        # Nếu có dấu (*) thì tô đỏ
        fg = "red" if "(*)" in label_text else "black"
        ttk.Label(parent, text=label_text, foreground=fg).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        
        entry = ttk.Entry(parent, width=30)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=5, pady=5)
        
        # Lưu lại widget entry vào dict để dùng trong hàm save
        if not hasattr(self, 'widget_map'): self.widget_map = {}
        self.widget_map[key] = entry

    def save_data(self):
        # 1. Lấy dữ liệu từ các ô nhập
        name = self.widget_map["name"].get().strip()
        phone = self.widget_map["phone"].get().strip()
        cccd = self.widget_map["cccd"].get().strip()
        dob = self.widget_map["dob"].get().strip()
        gender = self.combo_gender.get()

        # 2. VALIDATION (Kiểm tra bắt buộc)
        if not name or not phone or not cccd or not dob:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ các trường bắt buộc (*)")
            return

        # Gom dữ liệu JSON
        info_dict = {
            "phone": phone, "cccd": cccd, "dob": dob, "gender": gender,
            "address": self.widget_map["address"].get(),
            "insurance": self.widget_map["insurance"].get(),
            "history": self.widget_map["history"].get()
        }
        info_json = json.dumps(info_dict, ensure_ascii=False)

        try:
            self.controller.db.cursor.execute(
                "UPDATE users SET name = ?, info = ? WHERE username = ?", 
                (name, info_json, self.current_username)
            )
            self.controller.db.conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật hồ sơ thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))