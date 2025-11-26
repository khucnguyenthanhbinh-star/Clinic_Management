import tkinter as tk
from tkinter import ttk, messagebox, simpledialog # <--- Đã thêm simpledialog vào đây
from datetime import datetime, timedelta
import random

class ViewAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- HEADER ---
        header_frame = tk.Frame(self, bg="white", height=60)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="QUẢN LÝ LỊCH HẸN & CHECK-IN", font=("Arial", 16, "bold"), bg="white", fg="#007bff").pack(pady=15, padx=20, anchor="w")

        # --- MAIN CONTENT (SPLIT VIEW) ---
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#dddddd")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- CỘT TRÁI: DANH SÁCH (TABS) ---
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, width=450)

        self.tabs = ttk.Notebook(left_frame)
        self.tabs.pack(fill="both", expand=True)

        # Tab 1: Sắp tới
        self.tab_upcoming = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_upcoming, text="📅 Sắp tới")
        self.tree_up = self.create_treeview(self.tab_upcoming)

        # Tab 2: Lịch sử
        self.tab_history = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_history, text="Hồ sơ cũ")
        self.tree_his = self.create_treeview(self.tab_history)

        # Nút Refresh
        ttk.Button(left_frame, text="🔄 Làm mới danh sách", command=self.load_data).pack(fill="x", pady=5)

        # --- CỘT PHẢI: CHI TIẾT VÉ (E-TICKET) ---
        self.right_frame = tk.Frame(paned, bg="white", relief="sunken", bd=1)
        paned.add(self.right_frame)
        
        # Placeholder khi chưa chọn
        self.lbl_placeholder = tk.Label(self.right_frame, text="Chọn một lịch hẹn để xem chi tiết", bg="white", fg="gray")
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # Container chi tiết (Mặc định ẩn)
        self.detail_container = tk.Frame(self.right_frame, bg="white")
        
        # Load dữ liệu lần đầu
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
        tree.column("doctor", width=180)
        tree.column("status", width=100, anchor="center")
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Tag màu sắc
        tree.tag_configure("Da dat", foreground="#007bff") # Xanh dương
        tree.tag_configure("Unpaid", foreground="red")     # Đỏ
        tree.tag_configure("Hoan thanh", foreground="green")
        tree.tag_configure("Paid", foreground="green")
        tree.tag_configure("Da huy", foreground="gray")
        tree.tag_configure("Checked-in", foreground="#ffc107") # Vàng cam
        
        return tree

    def load_data(self):
        # Xóa cũ
        for item in self.tree_up.get_children(): self.tree_up.delete(item)
        for item in self.tree_his.get_children(): self.tree_his.delete(item)
        
        apts = self.controller.db.get_appointments(self.controller.auth.current_user)
        today = datetime.now().strftime("%Y-%m-%d")

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

            status = apt['status']
            date = apt['date']
            
            is_upcoming = (date >= today) and (status in ["Da dat", "Unpaid", "Checked-in"])
            
            values = (booking_code, date, apt['time'], doc_name, status)
            tags_data = (reason, str(apt['id'])) 
            
            if is_upcoming:
                self.tree_up.insert("", "end", values=values, tags=(status, *tags_data))
            else:
                self.tree_his.insert("", "end", values=values, tags=(status, *tags_data))

    def on_select(self, event):
        tree = event.widget
        selection = tree.selection()
        if not selection: return
        
        self.lbl_placeholder.place_forget()
        self.detail_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        item = tree.item(selection[0])
        vals = item['values']
        tags = item['tags']
        
        data = {
            "code": vals[0],
            "date": vals[1],
            "time": vals[2],
            "doctor": vals[3],
            "status": vals[4],
            "reason": tags[1],
            "real_id": tags[2]
        }
        self.render_detail(data)

    def render_detail(self, data):
        for w in self.detail_container.winfo_children(): w.destroy()
        
        # 1. HEADER VÉ
        top = tk.Frame(self.detail_container, bg="white")
        top.pack(fill="x")
        tk.Label(top, text="PHIẾU KHÁM ĐIỆN TỬ", font=("Arial", 10), bg="white", fg="gray").pack(anchor="w")
        tk.Label(top, text=f"MÃ SỐ: {data['code']}", font=("Arial", 18, "bold"), bg="white", fg="#007bff").pack(anchor="w")
        
        # 2. QR CODE
        qr_frame = tk.Frame(self.detail_container, bg="white", pady=10)
        qr_frame.pack(fill="x")
        
        canvas = tk.Canvas(qr_frame, width=120, height=120, bg="white", highlightthickness=0)
        canvas.pack(side="left")
        self.draw_fake_qr(canvas)
        
        info_f = tk.Frame(qr_frame, bg="white", padx=20)
        info_f.pack(side="left", fill="both", expand=True)
        
        user_name = self.controller.db.get_user(self.controller.auth.current_user)['name']
        tk.Label(info_f, text=f"Bệnh nhân: {user_name}", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(info_f, text=f"Ngày: {data['time']} - {data['date']}", bg="white", font=("Arial", 11)).pack(anchor="w", pady=5)
        tk.Label(info_f, text=f"Địa điểm: Cơ sở 1 - Tầng 2", bg="white", fg="gray").pack(anchor="w")

        # 3. STATUS STEPPER
        step_frame = tk.LabelFrame(self.detail_container, text="Trạng thái hồ sơ", bg="white", padx=10, pady=10)
        step_frame.pack(fill="x", pady=10)
        
        steps = ["Đã đặt", "Xác nhận", "Đã đến", "Hoàn thành"]
        current_st = data['status']
        
        st_idx = 0
        if current_st == "Unpaid": st_idx = 0
        elif current_st in ["Da dat", "Paid"]: st_idx = 1
        elif current_st == "Checked-in": st_idx = 2
        elif current_st == "Hoan thanh": st_idx = 3
        elif current_st == "Da huy": st_idx = -1
        
        if st_idx == -1:
            tk.Label(step_frame, text="❌ LỊCH HẸN ĐÃ BỊ HỦY", fg="red", bg="white", font=("Arial", 12, "bold")).pack()
        else:
            for i, step in enumerate(steps):
                color = "#28a745" if i <= st_idx else "#cccccc"
                font = ("Arial", 10, "bold") if i == st_idx else ("Arial", 10)
                icon = "◉" if i <= st_idx else "○"
                tk.Label(step_frame, text=f"{icon} {step}", fg=color, bg="white", font=font).pack(side="left", padx=10)

        # 4. ACTIONS
        action_frame = tk.Frame(self.detail_container, bg="white")
        action_frame.pack(fill="x", pady=20)
        
        if st_idx != -1 and st_idx < 3:
            ttk.Button(action_frame, text="📅 Đổi ngày/giờ", command=lambda: self.action_reschedule(data)).pack(side="left", padx=5, fill="x", expand=True)
            ttk.Button(action_frame, text="❌ Hủy lịch", command=lambda: self.action_cancel(data)).pack(side="left", padx=5, fill="x", expand=True)
            ttk.Button(action_frame, text="Add Calendar", command=lambda: self.action_add_calendar(data)).pack(side="left", padx=5)

        today = datetime.now().strftime("%Y-%m-%d")
        if data['date'] == today and st_idx < 2 and st_idx != -1:
             btn_checkin = tk.Button(self.detail_container, text="📲 CHECK-IN TẠI QUẦY (QR)", bg="#ffc107", fg="black", font=("Arial", 11, "bold"), command=lambda: self.action_checkin(data))
             btn_checkin.pack(fill="x", pady=5)

    def draw_fake_qr(self, canvas):
        canvas.delete("all")
        size = 10
        for r in range(12):
            for c in range(12):
                if random.choice([True, False]):
                    canvas.create_rectangle(c*size, r*size, (c+1)*size, (r+1)*size, fill="black")
        self.draw_finder(canvas, 0, 0, size)
        self.draw_finder(canvas, 0, 9, size)
        self.draw_finder(canvas, 9, 0, size)

    def draw_finder(self, canvas, r, c, size):
        x, y = c*size, r*size
        canvas.create_rectangle(x, y, x+3*size, y+3*size, fill="black")
        canvas.create_rectangle(x+size, y+size, x+2*size, y+2*size, fill="white")

    def action_cancel(self, data):
        # SỬA LỖI: Dùng simpledialog đã import
        reason = simpledialog.askstring("Hủy lịch", "Vui lòng nhập lý do hủy:", parent=self)
        if reason:
            confirm = messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn hủy? (Tiền cọc sẽ được hoàn vào Ví sau 24h)")
            if confirm:
                self.controller.db.cancel_appointment(data['real_id'])
                messagebox.showinfo("Thành công", "Đã hủy lịch hẹn.\nThông báo đã gửi tới bác sĩ.")
                self.load_data()
                self.detail_container.pack_forget()

    def action_reschedule(self, data):
        # SỬA LỖI: Dùng simpledialog đã import
        new_date = simpledialog.askstring("Đổi lịch", "Nhập ngày mới (YYYY-MM-DD):", parent=self)
        if new_date:
            try:
                self.controller.db.cursor.execute("UPDATE appointments SET date = ?, status = 'Da dat' WHERE id = ?", (new_date, data['real_id']))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", f"Đã đổi lịch sang ngày {new_date}.\nVui lòng đến đúng giờ!")
                self.load_data()
                self.detail_container.pack_forget()
            except:
                messagebox.showerror("Lỗi", "Ngày không hợp lệ!")

    def action_checkin(self, data):
        messagebox.showinfo("Quét mã", "Vui lòng đưa mã này cho Lễ tân hoặc máy quét...")
        self.controller.db.cursor.execute("UPDATE appointments SET status = 'Checked-in' WHERE id = ?", (data['real_id'],))
        self.controller.db.conn.commit()
        messagebox.showinfo("Thành công", "Check-in thành công!\nVui lòng ngồi chờ tại sảnh A.")
        self.load_data()
        self.detail_container.pack_forget()

    def action_add_calendar(self, data):
        title = f"Kham benh - {data['code']}"
        details = f"Bac si: {data['doctor']}"
        url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={data['date']}&details={details}"
        top = tk.Toplevel(self)
        top.title("Add to Calendar")
        ttk.Label(top, text="Copy link dưới đây:").pack(pady=10)
        e = ttk.Entry(top, width=50)
        e.insert(0, url)
        e.pack(padx=20, pady=10)