import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import random
import webbrowser
import urllib.parse

class ViewAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- BỘ TỪ ĐIỂN DỊCH TRẠNG THÁI ---
        self.STATUS_MAP = {
            "Da dat": "Đã đặt",
            "Unpaid": "Chưa thanh toán",
            "Hoan thanh": "Hoàn thành",
            "Paid": "Đã thanh toán",
            "Da huy": "Đã hủy",
            "Checked-in": "Đã check-in",
            "Confirmed": "Đã xác nhận",
            # Fallback cho trường hợp trong DB đã lỡ lưu có dấu
            "Đã đặt": "Đã đặt",
            "Đã hủy": "Đã hủy"
        }

        # --- HEADER ---
        header_frame = tk.Frame(self, bg="white", height=60)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="QUẢN LÝ LỊCH HẸN & CHECK-IN", font=("Arial", 16, "bold"), bg="white", fg="#007bff").pack(pady=15, padx=20, anchor="w")

        # --- MAIN CONTENT ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- CỘT TRÁI ---
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, width=480) # Tăng độ rộng để hiển thị chữ tiếng Việt rõ hơn

        self.tabs = ttk.Notebook(left_frame)
        self.tabs.pack(fill="both", expand=True)

        self.tab_upcoming = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_upcoming, text="📅 Sắp tới")
        self.tree_up = self.create_treeview(self.tab_upcoming)

        self.tab_history = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_history, text="Hồ sơ cũ")
        self.tree_his = self.create_treeview(self.tab_history)

        ttk.Button(left_frame, text="🔄 Làm mới danh sách", command=self.load_data).pack(fill="x", pady=5)

        # --- CỘT PHẢI ---
        self.right_frame = tk.Frame(paned, bg="white", relief="sunken", bd=1)
        paned.add(self.right_frame)
        
        self.lbl_placeholder = tk.Label(self.right_frame, text="Chọn một lịch hẹn để xem chi tiết", bg="white", fg="gray")
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self.detail_container = tk.Frame(self.right_frame, bg="white")
        
        self.load_data()

    def create_treeview(self, parent):
        cols = ("id", "date", "time", "doctor", "status")
        tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tree.heading("id", text="Mã")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("doctor", text="Bác sĩ / Dịch vụ")
        tree.heading("status", text="Trạng thái")
        
        tree.column("id", width=60, anchor="center")
        tree.column("date", width=90, anchor="center")
        tree.column("time", width=70, anchor="center")
        tree.column("doctor", width=150)
        tree.column("status", width=120, anchor="center") # Tăng độ rộng cột trạng thái
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Cấu hình màu sắc dựa trên MÃ GỐC (Raw Status) trong Database
        # Vì ta sẽ lưu Mã Gốc vào tags để xử lý logic
        tree.tag_configure("Da dat", foreground="#007bff") 
        tree.tag_configure("Đã đặt", foreground="#007bff")
        
        tree.tag_configure("Unpaid", foreground="red")     
        
        tree.tag_configure("Hoan thanh", foreground="green")
        tree.tag_configure("Paid", foreground="green")
        
        tree.tag_configure("Da huy", foreground="gray")
        tree.tag_configure("Đã hủy", foreground="gray")
        
        tree.tag_configure("Checked-in", foreground="#ffc107")
        
        return tree

    def load_data(self):
        for item in self.tree_up.get_children(): self.tree_up.delete(item)
        for item in self.tree_his.get_children(): self.tree_his.delete(item)
        
        apts = self.controller.db.get_appointments(self.controller.auth.current_user)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Nhóm trạng thái được coi là sắp tới
        upcoming_keys = ["Da dat", "Đã đặt", "Unpaid", "Checked-in", "Confirmed"]

        for apt in apts:
            reason = apt['reason']
            doc_name = "Bác sĩ"
            booking_code = f"#{apt['id']}"
            
            if "[" in reason:
                try:
                    parts = reason.split("]")
                    booking_code = parts[0].replace("[", "")
                    for p in parts:
                        if "BS" in p or "ThS" in p: doc_name = p.replace("[", "").strip()
                except: pass

            raw_status = apt['status'] # Lấy mã gốc: "Hoan thanh"
            display_status = self.STATUS_MAP.get(raw_status, raw_status) # Dịch sang: "Hoàn thành"
            
            date = apt['date']
            is_upcoming = (date >= today) and (raw_status in upcoming_keys)
            
            # Hiển thị display_status lên bảng, nhưng lưu raw_status vào tags để dùng cho màu sắc
            values = (booking_code, date, apt['time'], doc_name, display_status)
            tags_data = (reason, str(apt['id'])) 
            
            if is_upcoming:
                self.tree_up.insert("", "end", values=values, tags=(raw_status, *tags_data))
            else:
                self.tree_his.insert("", "end", values=values, tags=(raw_status, *tags_data))

    def on_select(self, event):
        tree = event.widget
        selection = tree.selection()
        if not selection: return
        
        self.lbl_placeholder.place_forget()
        self.detail_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        item = tree.item(selection[0])
        vals = item['values']
        tags = item['tags'] # tags[0] là raw_status
        
        data = {
            "code": vals[0], "date": vals[1], "time": vals[2],
            "doctor": vals[3], 
            "status_raw": tags[0], # Dùng mã gốc để xử lý logic (ẩn/hiện nút)
            "reason": tags[1], "real_id": tags[2]
        }
        self.render_detail(data)

    def render_detail(self, data):
        for w in self.detail_container.winfo_children(): w.destroy()
        
        top = tk.Frame(self.detail_container, bg="white")
        top.pack(fill="x")
        tk.Label(top, text="PHIẾU KHÁM ĐIỆN TỬ", font=("Arial", 10), bg="white", fg="gray").pack(anchor="w")
        tk.Label(top, text=f"MÃ SỐ: {data['code']}", font=("Arial", 18, "bold"), bg="white", fg="#007bff").pack(anchor="w")
        
        qr_frame = tk.Frame(self.detail_container, bg="white", pady=10)
        qr_frame.pack(fill="x")
        
        canvas = tk.Canvas(qr_frame, width=120, height=120, bg="white", highlightthickness=0)
        canvas.pack(side="left")
        self.draw_fake_qr(canvas)
        
        info_f = tk.Frame(qr_frame, bg="white", padx=20)
        info_f.pack(side="left", fill="both", expand=True)
        
        try: user_name = self.controller.db.get_user(self.controller.auth.current_user)['name']
        except: user_name = "Bệnh nhân"

        tk.Label(info_f, text=f"Bệnh nhân: {user_name}", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(info_f, text=f"Ngày: {data['time']} - {data['date']}", bg="white", font=("Arial", 11)).pack(anchor="w", pady=5)
        tk.Label(info_f, text=f"Địa điểm: Cơ sở 1 - Tầng 2", bg="white", fg="gray").pack(anchor="w")

        # STEPPER
        step_frame = tk.LabelFrame(self.detail_container, text="Trạng thái hồ sơ", bg="white", padx=10, pady=10)
        step_frame.pack(fill="x", pady=10)
        
        steps = ["Đã đặt", "Xác nhận", "Đã đến", "Hoàn thành"]
        current_st = data['status_raw'] # Dùng mã gốc để so sánh
        
        st_idx = 0
        if current_st == "Unpaid": st_idx = 0
        elif current_st in ["Da dat", "Đã đặt", "Paid"]: st_idx = 1
        elif current_st == "Checked-in": st_idx = 2
        elif current_st in ["Hoan thanh", "Hoàn thành"]: st_idx = 3
        elif current_st in ["Da huy", "Đã hủy"]: st_idx = -1
        
        if st_idx == -1:
            tk.Label(step_frame, text="❌ LỊCH HẸN ĐÃ BỊ HỦY", fg="red", bg="white", font=("Arial", 12, "bold")).pack()
        else:
            for i, step in enumerate(steps):
                color = "#28a745" if i <= st_idx else "#cccccc"
                font = ("Arial", 10, "bold") if i == st_idx else ("Arial", 10)
                icon = "◉" if i <= st_idx else "○"
                tk.Label(step_frame, text=f"{icon} {step}", fg=color, bg="white", font=font).pack(side="left", padx=10)

        action_frame = tk.Frame(self.detail_container, bg="white")
        action_frame.pack(fill="x", pady=20)
        
        if st_idx != -1 and st_idx < 3:
            ttk.Button(action_frame, text="📅 Đổi ngày/giờ", command=lambda: self.show_reschedule_dialog(data)).pack(side="left", padx=5, fill="x", expand=True)
            ttk.Button(action_frame, text="❌ Hủy lịch", command=lambda: self.action_cancel(data)).pack(side="left", padx=5, fill="x", expand=True)
            ttk.Button(action_frame, text="Thêm vào Lịch", command=lambda: self.action_add_calendar(data)).pack(side="left", padx=5)

        today = datetime.now().strftime("%Y-%m-%d")
        if data['date'] == today and st_idx < 2 and st_idx != -1:
             btn_checkin = tk.Button(self.detail_container, text="📲 CHECK-IN TẠI QUẦY (QR)", bg="#ffc107", fg="black", font=("Arial", 11, "bold"), command=lambda: self.action_checkin(data))
             btn_checkin.pack(fill="x", pady=5)

    def draw_fake_qr(self, canvas):
        canvas.delete("all"); size = 10
        for r in range(12):
            for c in range(12):
                if random.choice([True, False]): canvas.create_rectangle(c*size, r*size, (c+1)*size, (r+1)*size, fill="black")
        for r,c in [(0,0), (0,9), (9,0)]:
            x, y = c*size, r*size
            canvas.create_rectangle(x, y, x+3*size, y+3*size, fill="black")
            canvas.create_rectangle(x+size, y+size, x+2*size, y+2*size, fill="white")

    def action_cancel(self, data):
        reason = simpledialog.askstring("Hủy lịch", "Vui lòng nhập lý do hủy:", parent=self)
        if reason:
            if messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn hủy? (Tiền cọc sẽ được hoàn vào Ví sau 24h)"):
                self.controller.db.cursor.execute("UPDATE appointments SET status = 'Đã hủy' WHERE id = ?", (data['real_id'],))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Đã hủy lịch hẹn.")
                self.load_data(); self.detail_container.pack_forget()

    def show_reschedule_dialog(self, data):
        dialog = tk.Toplevel(self); dialog.title("Đổi lịch khám"); dialog.geometry("350x250")
        ttk.Label(dialog, text="Chọn thời gian mới:", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(dialog, text="Ngày khám:").pack(anchor="w", padx=30)
        date_combo = ttk.Combobox(dialog, state="readonly", width=30)
        dates = []; real_dates = []
        for i in range(1, 31):
            d = datetime.now() + timedelta(days=i)
            dates.append(d.strftime("%d/%m/%Y (%A)")); real_dates.append(d.strftime("%Y-%m-%d"))
        date_combo['values'] = dates; date_combo.current(0); date_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Giờ khám:").pack(anchor="w", padx=30)
        time_combo = ttk.Combobox(dialog, state="readonly", width=30)
        time_combo['values'] = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "14:00", "14:30", "15:00", "15:30", "16:00"]
        time_combo.current(0); time_combo.pack(pady=5)
        
        def confirm():
            try:
                self.controller.db.cursor.execute("UPDATE appointments SET date = ?, time = ?, status = 'Đã đặt' WHERE id = ?", 
                                                  (real_dates[date_combo.current()], time_combo.get(), data['real_id']))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Đã đổi lịch."); dialog.destroy(); self.load_data(); self.detail_container.pack_forget()
            except Exception as e: messagebox.showerror("Lỗi", str(e))
        ttk.Button(dialog, text="Lưu thay đổi", command=confirm).pack(pady=20)

    def action_checkin(self, data):
        messagebox.showinfo("Quét mã", "Vui lòng đưa mã này cho Lễ tân..."); 
        self.controller.db.cursor.execute("UPDATE appointments SET status = 'Checked-in' WHERE id = ?", (data['real_id'],)); 
        self.controller.db.conn.commit(); 
        messagebox.showinfo("Thành công", "Check-in thành công!"); self.load_data(); self.detail_container.pack_forget()

    def action_add_calendar(self, data):
        try:
            start_dt = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(hours=1)
            fmt_google = "%Y%m%dT%H%M00"
            dates_param = f"{start_dt.strftime(fmt_google)}/{end_dt.strftime(fmt_google)}"
            title = urllib.parse.quote(f"Khám bệnh: {data['doctor']}")
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={dates_param}"
            webbrowser.open(url)
        except: messagebox.showerror("Lỗi", "Không thể tạo link")