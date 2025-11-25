import tkinter as tk
from tkinter import ttk, messagebox

class AdminViewManager:
    def __init__(self, master_app, controller):
        self.master_app = master_app
        self.controller = controller

    def show_dashboard(self):
        self.master_app.clear_frame()
        self.master_app.add_menu()
        tk.Label(self.master_app, text="DASHBOARD QUẢN TRỊ VIÊN", font=("Arial", 16, "bold")).pack(pady=10)
        nb = ttk.Notebook(self.master_app); nb.pack(fill='both', expand=True)

        # --- TAB 1: QUẢN LÝ TÀI KHOẢN (User Management) ---
        t_users = tk.Frame(nb)
        nb.add(t_users, text="Quản lý Tài khoản")
        
        # Danh sách User (Bỏ cột Pass)
        tree_user = ttk.Treeview(t_users, columns=("ID", "User", "Role", "Name", "Spec"), show="headings", height=8)
        tree_user.heading("ID", text="ID"); tree_user.column("ID", width=40)
        tree_user.heading("User", text="Username"); tree_user.column("User", width=120)
        tree_user.heading("Role", text="Role"); tree_user.column("Role", width=80)
        tree_user.heading("Name", text="Tên"); tree_user.column("Name", width=180)
        tree_user.heading("Spec", text="Chuyên khoa"); tree_user.column("Spec", width=120)
        tree_user.pack(fill='x', padx=5, pady=5)

        def load_users():
            tree_user.delete(*tree_user.get_children())
            users = self.controller.get_all_users_admin()
            for u in users: 
                # Bỏ u[2] (password_hash) khỏi values khi chèn vào treeview
                tree_user.insert("", "end", iid=u[0], values=(u[0], u[1], u[3], u[4], u[5]))
        load_users()
        
        tk.Label(t_users, text="Chú ý: Chọn tài khoản bên dưới để đặt lại mật khẩu hoặc xóa.", fg="red").pack(pady=5)


        # Form thêm Tài khoản (Chung cho 3 role)
        f_add_user = tk.LabelFrame(t_users, text="Thêm Tài khoản Mới")
        f_add_user.pack(fill='x', padx=5, pady=5)
        
        # Role selection
        tk.Label(f_add_user, text="Loại tài khoản:").grid(row=0, column=0, sticky='w', padx=5)
        cb_role = ttk.Combobox(f_add_user, values=["doctor", "patient", "admin"], state="readonly", width=10)
        cb_role.set("doctor")
        cb_role.grid(row=0, column=1, padx=5)

        # Các trường chung
        tk.Label(f_add_user, text="Username:").grid(row=0, column=2, sticky='w', padx=5)
        entry_u = tk.Entry(f_add_user, width=15); entry_u.grid(row=0, column=3, padx=5)
        
        tk.Label(f_add_user, text="Password:").grid(row=1, column=0, sticky='w', padx=5)
        entry_p = tk.Entry(f_add_user, width=15); entry_p.grid(row=1, column=1, padx=5)
        
        tk.Label(f_add_user, text="Họ tên:").grid(row=1, column=2, sticky='w', padx=5)
        entry_n = tk.Entry(f_add_user, width=20); entry_n.grid(row=1, column=3, padx=5)

        # Các trường riêng biệt cho Doctor (Khởi tạo và quản lý vị trí)
        lbl_s = tk.Label(f_add_user, text="Chuyên khoa:")
        cb_spec = ttk.Combobox(f_add_user, values=["Chuyên khoa 1", "Chuyên khoa 2", "Chuyên khoa 3"], width=15); cb_spec.set("Chuyên khoa 1")
        
        def toggle_doctor_fields(event=None):
            role = cb_role.get()
            if role == 'doctor':
                lbl_s.grid(row=2, column=0, sticky='w', padx=5)
                cb_spec.grid(row=2, column=1, padx=5)
            else:
                lbl_s.grid_forget()
                cb_spec.grid_forget()
        
        cb_role.bind("<<ComboboxSelected>>", toggle_doctor_fields)
        toggle_doctor_fields()

        def add_user_action():
            role = cb_role.get()
            username = entry_u.get()
            password = entry_p.get()
            fullname = entry_n.get()
            spec = cb_spec.get() if role == 'doctor' else None

            if not username or not password or not fullname:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
                return

            success, msg = self.controller.add_user_admin(
                role, username, password, fullname, spec
            )
            if success:
                messagebox.showinfo("Thành công", msg)
                load_users()
            else:
                messagebox.showerror("Lỗi", msg)
        
        tk.Button(f_add_user, text="Thêm Tài khoản", command=add_user_action).grid(row=3, column=1, columnspan=2, pady=10)


        # --- CÁC NÚT THAO TÁC (RESET/DELETE) ---
        f_ops = tk.Frame(t_users)
        f_ops.pack(fill='x', padx=5, pady=5)

        def reset_password_popup():
            sel = tree_user.selection()
            if not sel: 
                messagebox.showerror("Lỗi", "Vui lòng chọn một tài khoản để Reset.")
                return

            item = tree_user.item(sel[0])
            uid = item['values'][0]
            username = item['values'][1]
            
            popup = tk.Toplevel(self.master_app)
            popup.title(f"Reset Mật khẩu cho {username}")
            popup.geometry("300x150")

            tk.Label(popup, text=f"Đặt lại mật khẩu cho: {username}", font=("Arial", 10, "bold")).pack(pady=10)
            
            tk.Label(popup, text="Mật khẩu mới:").pack()
            new_pass_entry = tk.Entry(popup, show="*")
            new_pass_entry.pack()

            def confirm_reset():
                new_pass = new_pass_entry.get()
                success, msg = self.controller.reset_user_password(uid, new_pass)
                if success:
                    messagebox.showinfo("Thành công", f"Mật khẩu của {username} đã được đặt lại.")
                    load_users()
                    popup.destroy()
                else:
                    messagebox.showerror("Lỗi", msg)
            
            tk.Button(popup, text="Xác nhận Reset", command=confirm_reset, bg="#FFC107").pack(pady=10)
            

        tk.Button(f_ops, text="Reset Mật khẩu", command=reset_password_popup, bg="#FFC107").pack(side='left', padx=10)
        
        def delete_user_action():
            sel = tree_user.selection()
            if not sel: return
            item = tree_user.item(sel[0])
            uid = item['values'][0]
            role = item['values'][2] 
            if role == 'admin' and item['values'][1] == 'admin':
                messagebox.showwarning("Cảnh báo", "Không thể xóa Admin gốc!")
                return
            if messagebox.askyesno("Xác nhận", f"Xóa user ID {uid} ({role})?"):
                if self.controller.delete_user(uid):
                    load_users()
                else: messagebox.showerror("Lỗi", "Không thể xóa.")

        tk.Button(f_ops, text="Xóa Tài khoản", bg="red", fg="white", command=delete_user_action).pack(side='left', padx=10)


        # --- TAB 2: QUẢN LÝ KHO THUỐC (Inventory Management) ---
        t_meds = tk.Frame(nb)
        nb.add(t_meds, text="Quản lý Kho thuốc")
        
        tree_med = ttk.Treeview(t_meds, columns=("ID", "Name", "Price", "Stock"), show="headings", height=8)
        tree_med.heading("ID", text="ID"); tree_med.column("ID", width=40)
        tree_med.heading("Name", text="Tên thuốc"); tree_med.column("Name", width=200)
        tree_med.heading("Price", text="Giá"); tree_med.column("Price", width=100)
        tree_med.heading("Stock", text="Tồn kho"); tree_med.column("Stock", width=100)
        tree_med.pack(fill='x', padx=5, pady=5)
        
        def refresh_meds():
            tree_med.delete(*tree_med.get_children())
            self.controller.cursor.execute("SELECT id, name, price, stock FROM Medicines")
            for r in self.controller.cursor.fetchall(): tree_med.insert("", "end", values=r)
        refresh_meds()
        
        # Form Chi tiết Thuốc
        f_inv = tk.LabelFrame(t_meds, text="Chi tiết Thuốc (Thêm / Sửa)")
        f_inv.pack(fill='x', padx=5, pady=5)
        
        v_mid = tk.StringVar(); v_mname = tk.StringVar(); v_mprice = tk.StringVar(); v_mstock = tk.StringVar()

        tk.Label(f_inv, text="ID:").grid(row=0, column=0); tk.Entry(f_inv, textvariable=v_mid, state='readonly').grid(row=0, column=1)
        tk.Label(f_inv, text="Tên:").grid(row=0, column=2); tk.Entry(f_inv, textvariable=v_mname).grid(row=0, column=3)
        tk.Label(f_inv, text="Giá:").grid(row=1, column=0); tk.Entry(f_inv, textvariable=v_mprice).grid(row=1, column=1)
        tk.Label(f_inv, text="Tồn:").grid(row=1, column=2); tk.Entry(f_inv, textvariable=v_mstock).grid(row=1, column=3)

        def select_med(event):
            sel = tree_med.selection()
            if not sel: return
            vals = tree_med.item(sel[0])['values']
            v_mid.set(vals[0]); v_mname.set(vals[1]); v_mprice.set(vals[2]); v_mstock.set(vals[3])
        tree_med.bind("<<TreeviewSelect>>", select_med)

        def add_med_action():
            if self.controller.add_medicine(v_mname.get(), v_mprice.get(), v_mstock.get()): refresh_meds(); messagebox.showinfo("OK", "Đã thêm.")
            else: messagebox.showerror("Lỗi", "Lỗi thêm.")
        def update_med_action():
            if not v_mid.get(): return
            if self.controller.update_medicine(v_mid.get(), v_mname.get(), v_mprice.get(), v_mstock.get()): refresh_meds(); messagebox.showinfo("OK", "Đã sửa.")
            else: messagebox.showerror("Lỗi", "Lỗi sửa.")
        def delete_med_action():
            if not v_mid.get(): return
            if messagebox.askyesno("Xóa", "Xóa thuốc này?"): self.controller.delete_medicine(v_mid.get()); refresh_meds(); v_mid.set(""); v_mname.set("")

        tk.Button(f_inv, text="Thêm", command=add_med_action).grid(row=2, column=1, pady=5)
        tk.Button(f_inv, text="Sửa", command=update_med_action).grid(row=2, column=2, pady=5)
        tk.Button(f_inv, text="Xóa", fg="red", command=delete_med_action).grid(row=2, column=3, pady=5)


        # --- TAB 3: QUẢN LÝ LỊCH HẸN (Appointment Management) ---
        t_appt = tk.Frame(nb)
        nb.add(t_appt, text="Quản lý Lịch hẹn")
        
        tree_all_appt = ttk.Treeview(t_appt, columns=("ID", "Date", "Time", "Patient", "Doctor", "Status"), show="headings", height=10)
        for col in ["ID", "Date", "Time", "Patient", "Doctor", "Status"]:
            tree_all_appt.heading(col, text=col)
            tree_all_appt.column(col, width=100)
        tree_all_appt.column("Patient", width=150); tree_all_appt.column("Doctor", width=150)
        tree_all_appt.pack(fill='both', expand=True, padx=5, pady=5)

        def load_all_appts():
            tree_all_appt.delete(*tree_all_appt.get_children())
            appts = self.controller.get_all_appointments_admin()
            for a in appts: tree_all_appt.insert("", "end", values=a)
        load_all_appts()

        def admin_cancel_appt():
            sel = tree_all_appt.selection()
            if not sel: return
            item = tree_all_appt.item(sel[0])
            aid = item['values'][0]; status = item['values'][5]
            if status == 'Completed': messagebox.showerror("Lỗi", "Không thể hủy lịch đã hoàn thành."); return
            if self.controller.cancel_appointment(aid): load_all_appts(); messagebox.showinfo("OK", "Đã hủy lịch hẹn.")

        tk.Button(t_appt, text="Hủy Lịch Hẹn", fg="red", command=admin_cancel_appt).pack(pady=5)
        tk.Button(t_appt, text="Làm mới danh sách", command=load_all_appts).pack(pady=5)


        # --- TAB 4: BÁO CÁO (Reporting) ---
        t_report = tk.Frame(nb)
        nb.add(t_report, text="Báo cáo Doanh thu")
        
        rev = self.controller.get_revenue()
        tk.Label(t_report, text=f"TỔNG DOANH THU ĐÃ THANH TOÁN (PAID)", font=("Arial", 14)).pack(pady=20)
        tk.Label(t_report, text=f"{rev:,.0f} VND", font=("Arial", 24, "bold"), fg="green").pack(pady=10)
        tk.Label(t_report, text="(Chỉ tính các hóa đơn có trạng thái 'Paid')").pack()