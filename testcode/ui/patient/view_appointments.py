import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ViewAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Tiêu đề
        ttk.Label(self, text="QUẢN LÝ LỊCH HẸN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # --- DANH SÁCH LỊCH HẸN ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        # Thêm cột ID để xử lý logic (nhưng có thể ẩn đi hoặc để cột nhỏ)
        columns = ("id", "date", "time", "reason", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="Mã")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("reason", text="Chi tiết / Bác sĩ")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("reason", width=350)
        self.tree.column("status", width=120, anchor="center")
        
        # Cấu hình màu sắc cho các trạng thái
        self.tree.tag_configure("upcoming", foreground="blue")       # Sắp tới
        self.tree.tag_configure("completed", foreground="green")     # Hoàn thành
        self.tree.tag_configure("cancelled", foreground="gray")      # Đã hủy
        
        self.tree.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- THANH CÔNG CỤ (BUTTONS) ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Làm mới danh sách", command=self.load_data).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Hủy cuộc hẹn", command=self.cancel_booking).pack(side="left", padx=10)

        # Load dữ liệu ban đầu
        self.load_data()

    def load_data(self):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Lấy dữ liệu từ DB
        appointments = self.controller.db.get_appointments(self.controller.auth.current_user)
        
        # Sắp xếp: Ngày giảm dần (Mới nhất lên đầu)
        appointments.sort(key=lambda x: x['date'], reverse=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for apt in appointments:
            # Xác định tag màu sắc
            tag = "upcoming"
            status = apt["status"]
            date = apt["date"]
            
            if status == "Đã hủy":
                tag = "cancelled"
            elif status == "Hoan thanh" or status == "Paid":
                tag = "completed"
                status = "Đã hoàn thành"
            elif date < today:
                tag = "cancelled" # Quá khứ mà chưa hoàn thành coi như trôi qua
                if status == "Đã đặt": status = "Đã qua (Vắng mặt)"
            
            self.tree.insert("", "end", values=(apt["id"], apt["date"], apt["time"], apt["reason"], status), tags=(tag,))

    def cancel_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lịch hẹn để hủy!")
            return
        
        # Lấy thông tin dòng đang chọn
        item = self.tree.item(selected[0])
        values = item['values']
        apt_id = values[0]
        date_str = values[1]
        status = values[4]
        
        # --- KIỂM TRA ĐIỀU KIỆN HỦY ---
        
        # 1. Không hủy lịch đã qua hoặc đã hoàn thành/hủy
        if status != "Đã đặt" and status != "Unpaid":
            messagebox.showerror("Lỗi", f"Không thể hủy lịch hẹn đang ở trạng thái: {status}")
            return

        # 2. Không hủy lịch quá khứ
        try:
            apt_date = datetime.strptime(date_str, "%Y-%m-%d")
            current_date = datetime.now()
            if apt_date.date() < current_date.date():
                messagebox.showerror("Lỗi", "Không thể hủy lịch hẹn trong quá khứ!")
                return
        except: pass

        # Hộp thoại xác nhận
        confirm = messagebox.askyesno("Xác nhận hủy", 
                                      f"Bạn có chắc chắn muốn hủy lịch hẹn ngày {date_str} không?\n\nHành động này không thể hoàn tác.")
        
        if confirm:
            # Gọi DB để update status
            self.controller.db.cancel_appointment(apt_id)
            messagebox.showinfo("Thành công", "Đã hủy lịch hẹn thành công!")
            self.load_data() # Tải lại bảng