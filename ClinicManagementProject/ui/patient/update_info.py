import tkinter as tk
from tkinter import ttk, messagebox
import json
import re # Thư viện xử lý biểu thức chính quy (Regex)
from datetime import datetime # Thư viện xử lý ngày tháng

class UpdateInfoView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_username = self.controller.auth.current_user
        
        # --- SỬA TIÊU ĐỀ TẠI ĐÂY ---
        tk.Label(self, text="CẬP NHẬT THÔNG TIN CÁ NHÂN", font=("Arial", 16, "bold"), foreground="#007bff").pack(pady=20)
        
        # Canvas cuộn
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load dữ liệu từ DB
        user_row = self.controller.db.get_user(self.current_username)
        self.current_name = user_row['name']
        raw_info = user_row['info']
        self.data = {}
        try:
            self.data = json.loads(raw_info) if raw_info else {}
        except:
            self.data = {}

        # --- FORM NHẬP LIỆU ---
        self.widget_map = {} 

        # Nhóm 1: Thông tin BẮT BUỘC
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
        
        # Giới tính
        ttk.Label(group_req, text="Giới tính (*):", foreground="red").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.combo_gender = ttk.Combobox(group_req, values=["Nam", "Nữ", "Khác"], width=27, state="readonly")
        gender_val = self.data.get("gender", "Nam")
        self.combo_gender.set(gender_val if gender_val else "Nam")
        self.combo_gender.grid(row=4, column=1, padx=5, pady=5)

        # Nhóm 2: Thông tin BỔ SUNG
        group_opt = ttk.LabelFrame(self.scrollable_frame, text="Thông tin bổ sung", padding=15)
        group_opt.pack(fill="x", padx=20, pady=10)

        self.create_row(group_opt, 0, "Địa chỉ:", self.data.get("address", ""), "address")
        self.create_row(group_opt, 1, "Mã BHYT:", self.data.get("insurance", ""), "insurance")
        self.create_row(group_opt, 2, "Tiền sử bệnh / Dị ứng:", self.data.get("history", ""), "history")

        # Nút Lưu
        ttk.Button(self.scrollable_frame, text="Lưu hồ sơ", command=self.save_data).pack(pady=20, ipadx=20)

    def create_row(self, parent, row, label_text, value, key):
        fg = "red" if "(*)" in label_text else "black"
        ttk.Label(parent, text=label_text, foreground=fg).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(parent, width=30)
        entry.insert(0, str(value) if value else "")
        entry.grid(row=row, column=1, padx=5, pady=5)
        self.widget_map[key] = entry

    def save_data(self):
        # 1. Lấy dữ liệu thô
        name = self.widget_map["name"].get().strip()
        phone = self.widget_map["phone"].get().strip()
        cccd = self.widget_map["cccd"].get().strip()
        dob = self.widget_map["dob"].get().strip()
        gender = self.combo_gender.get()
        
        address = self.widget_map["address"].get().strip()
        insurance = self.widget_map["insurance"].get().strip()
        history = self.widget_map["history"].get().strip()

        # ================== KIỂM TRA HỢP LỆ (VALIDATION) ==================
        
        # 1. Kiểm tra rỗng
        if not name or not phone or not cccd or not dob:
            return messagebox.showerror("Thiếu thông tin", "Vui lòng điền tất cả các trường có dấu (*)")

        # 2. Kiểm tra Số điện thoại (VN: 10-11 số, bắt đầu bằng 0)
        if not re.match(r"^0\d{9,10}$", phone):
            return messagebox.showerror("Lỗi định dạng", "Số điện thoại không hợp lệ!\n(Phải là số, bắt đầu bằng 0, từ 10-11 số)")

        # 3. Kiểm tra CCCD (9 hoặc 12 số)
        if not re.match(r"^\d{9}$|^\d{12}$", cccd):
            return messagebox.showerror("Lỗi định dạng", "Số CCCD/CMND không hợp lệ!\n(Phải là 9 hoặc 12 chữ số)")

        # 4. Kiểm tra Ngày sinh (Phải đúng lịch và format dd/mm/yyyy)
        try:
            dob_date = datetime.strptime(dob, "%d/%m/%Y")
            
            if dob_date > datetime.now():
                return messagebox.showerror("Lỗi logic", "Ngày sinh không được lớn hơn ngày hiện tại!")
                
            if datetime.now().year - dob_date.year > 120:
                return messagebox.showwarning("Cảnh báo", "Năm sinh có vẻ không chính xác (Quá lớn tuổi).")
                
        except ValueError:
            return messagebox.showerror("Lỗi định dạng", "Ngày sinh không hợp lệ!\nVui lòng nhập đúng định dạng: dd/mm/yyyy (Ví dụ: 15/05/1990)")

        # ================== LƯU DỮ LIỆU ==================
        
        info_dict = {
            "phone": phone, "cccd": cccd, "dob": dob, "gender": gender,
            "address": address, "insurance": insurance, "history": history
        }
        info_json = json.dumps(info_dict, ensure_ascii=False)

        try:
            self.controller.db.cursor.execute(
                "UPDATE users SET name = ?, info = ? WHERE username = ?", 
                (name, info_json, self.current_username)
            )
            self.controller.db.conn.commit()
            
            messagebox.showinfo("Thành công", "Cập nhật hồ sơ thành công!")
            
            # Quay về trang chủ
            from ui.patient.patient_dashboard import PatientDashboardView
            for w in self.master.winfo_children(): w.destroy()
            PatientDashboardView(self.master, self.controller).pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Lỗi Database", str(e))