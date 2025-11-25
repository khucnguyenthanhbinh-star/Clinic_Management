import tkinter as tk
from tkinter import ttk, messagebox
import json

class DoctorViewManager:
    def __init__(self, master_app, controller, doctor_id):
        self.master_app = master_app
        self.controller = controller
        self.current_user_id = doctor_id
        self.current_exam_app_id = None
        self.current_patient_id = None
        self.exam_meds = []
        self.exam_tests = []
        self.patient_info_widgets = {}

    def show_dashboard(self):
        self.master_app.clear_frame()
        self.master_app.add_menu()
        
        main_paned = ttk.PanedWindow(self.master_app, orient=tk.HORIZONTAL)
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)

        left_column = ttk.Frame(main_paned, width=350); main_paned.add(left_column)
        right_column = ttk.Frame(main_paned); main_paned.add(right_column)
        
        self._build_left_column(left_column)
        self._build_right_column(right_column)

    # --- Xây dựng cột TRÁI (Danh sách chờ & Hồ sơ) ---
    def _build_left_column(self, frame):
        tk.Label(frame, text="DANH SÁCH LỊCH HẸN CHỜ", font=("Arial", 11, "bold")).pack(pady=5)
        self.tree_wait = ttk.Treeview(frame, columns=("ID", "Name", "Time"), show="headings", height=8)
        self.tree_wait.heading("ID", text="AppID"); self.tree_wait.column("ID", width=40, anchor='center')
        self.tree_wait.heading("Name", text="Bệnh nhân"); self.tree_wait.column("Name", width=150)
        self.tree_wait.heading("Time", text="Giờ"); self.tree_wait.column("Time", width=80, anchor='center')
        self.tree_wait.pack(fill='x', padx=5, pady=5)
        self.load_appointments()

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=5)
        tk.Label(frame, text="HỒ SƠ BỆNH NHÂN", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.patient_notebook = ttk.Notebook(frame)
        self.patient_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        tab_info = ttk.Frame(self.patient_notebook); self.patient_notebook.add(tab_info, text="Thông tin")
        tab_history = ttk.Frame(self.patient_notebook); self.patient_notebook.add(tab_history, text="Lịch sử")
        
        self._build_patient_info_display(tab_info)
        self._build_patient_history_display(tab_history)

        self.tree_wait.bind("<<TreeviewSelect>>", self._select_patient_for_exam)
        
    def load_appointments(self):
        self.tree_wait.delete(*self.tree_wait.get_children())
        apps = self.controller.get_doctor_appointments(self.current_user_id)
        for a in apps:
            self.tree_wait.insert("", "end", iid=a[0], values=(a[0], a[1], f"{a[3]} ({a[2]})"))
    
    def _select_patient_for_exam(self, event):
        sel = self.tree_wait.focus()
        if not sel: return
        item = self.tree_wait.item(sel)
        app_id = int(item['values'][0])
        
        patient_id = self.controller.cursor.execute("SELECT patient_id FROM Appointments WHERE id=?", (app_id,)).fetchone()[0]
        
        self.current_exam_app_id = app_id
        self.current_patient_id = patient_id
        
        self.controller.start_examination(app_id)
        self._load_patient_data(patient_id)
        self.lbl_status.config(text=f"Đang khám: {item['values'][1]} (ID: {app_id})", fg="blue")

    def _load_patient_data(self, patient_id):
        info = self.controller.get_patient_info(patient_id)
        self.patient_info_widgets['Name'].config(text=f"Tên: {info[1] or 'N/A'}")
        self.patient_info_widgets['DOB'].config(text=f"NS: {info[4] or 'N/A'}")
        self.patient_info_widgets['Addr'].config(text=f"ĐC: {info[5] or 'N/A'}")
        self.patient_info_widgets['Hist'].config(text=f"Tiền sử: {info[6] or 'Không'}", wraplength=300)
        
        self.tree_history.delete(*self.tree_history.get_children())
        history = self.controller.get_patient_records(patient_id)
        for i, r in enumerate(history):
            self.tree_history.insert("", tk.END, iid=i, values=(r[0], r[1], r[2] or "Chưa có"))
        
        self.exam_meds = []; self.exam_tests = []
        self.lb_pres.delete(0, tk.END)
        self.txt_diag.delete("1.0", tk.END)
        
    def _build_patient_info_display(self, frame):
        self.patient_info_widgets['Name'] = tk.Label(frame, text="Tên: --", justify=tk.LEFT)
        self.patient_info_widgets['Name'].pack(fill='x', pady=2, padx=5)
        self.patient_info_widgets['DOB'] = tk.Label(frame, text="NS: --", justify=tk.LEFT)
        self.patient_info_widgets['DOB'].pack(fill='x', pady=2, padx=5)
        self.patient_info_widgets['Addr'] = tk.Label(frame, text="ĐC: --", justify=tk.LEFT)
        self.patient_info_widgets['Addr'].pack(fill='x', pady=2, padx=5)
        self.patient_info_widgets['Hist'] = tk.Label(frame, text="Tiền sử: --", justify=tk.LEFT)
        self.patient_info_widgets['Hist'].pack(fill='x', pady=2, padx=5)

    def _build_patient_history_display(self, frame):
        self.tree_history = ttk.Treeview(frame, columns=("Date", "Doc", "Diag"), show="headings")
        self.tree_history.heading("Date", text="Ngày"); self.tree_history.column("Date", width=80)
        self.tree_history.heading("Doc", text="Bác sĩ"); self.tree_history.column("Doc", width=100)
        self.tree_history.heading("Diag", text="Chẩn đoán"); self.tree_history.column("Diag", width=120)
        self.tree_history.pack(fill='both', expand=True)

    # --- Xây dựng cột PHẢI (Quy trình Khám) ---
    def _build_right_column(self, frame):
        self.lbl_status = tk.Label(frame, text="Chưa chọn bệnh nhân", font=("Arial", 12, "bold"), fg="blue"); self.lbl_status.pack(pady=10)
        
        self.exam_notebook = ttk.Notebook(frame)
        self.exam_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        tab_diag = ttk.Frame(self.exam_notebook); self.exam_notebook.add(tab_diag, text="1. Chẩn đoán")
        tab_tests = ttk.Frame(self.exam_notebook); self.exam_notebook.add(tab_tests, text="2. Xét nghiệm")
        tab_meds = ttk.Frame(self.exam_notebook); self.exam_notebook.add(tab_meds, text="3. Kê đơn")
        
        self._build_diagnosis_tab(tab_diag)
        self._build_test_tab(tab_tests)
        self._build_medication_tab(tab_meds)

        tk.Button(frame, text="HOÀN TẤT KHÁM & TẠO HÓA ĐƠN", bg="green", fg="white", font=("bold"), command=self._complete_examination).pack(pady=10, fill='x')

    def _build_diagnosis_tab(self, frame):
        tk.Label(frame, text="CHẨN ĐOÁN VÀ KẾT LUẬN CUỐI", font=("bold")).pack(pady=10)
        self.txt_diag = tk.Text(frame, height=15)
        self.txt_diag.pack(fill='both', expand=True)

    def _build_test_tab(self, frame):
        tk.Label(frame, text="CHỈ ĐỊNH XÉT NGHIỆM", font=("bold")).pack(pady=10)
        self.controller.cursor.execute("SELECT id, name, price FROM Tests")
        all_tests = self.controller.cursor.fetchall()
        
        self.test_vars = {}
        for test_id, name, price in all_tests:
            var = tk.IntVar()
            chk = tk.Checkbutton(frame, text=f"{name} ({price:,.0f} VND)", variable=var)
            chk.pack(anchor='w')
            self.test_vars[test_id] = {'name': name, 'price': price, 'var': var}

        def confirm_tests():
            if not self.current_exam_app_id: return
            self.exam_tests = [{'name': data['name']} for data in self.test_vars.values() if data['var'].get() == 1]
            self.controller.update_test_results(self.current_exam_app_id, self.exam_tests)
            messagebox.showinfo("OK", f"Đã chỉ định {len(self.exam_tests)} xét nghiệm và cập nhật hồ sơ.")
        
        tk.Button(frame, text="Lưu Chỉ Định Xét Nghiệm", command=confirm_tests).pack(pady=10)
        
    def _build_medication_tab(self, frame):
        tk.Label(frame, text="KÊ ĐƠN THUỐC", font=("bold")).pack(pady=10)
        
        f_controls = ttk.Frame(frame)
        f_controls.pack(fill='x', pady=5)
        
        self.controller.cursor.execute("SELECT name, stock FROM Medicines")
        med_rows = self.controller.cursor.fetchall()
        med_names = [m[0] for m in med_rows]
        
        tk.Label(f_controls, text="Thuốc:").pack(side='left')
        self.cb_med = ttk.Combobox(f_controls, values=med_names); self.cb_med.pack(side='left', padx=5)
        tk.Label(f_controls, text="Số lượng:").pack(side='left')
        self.sp_qty = tk.Spinbox(f_controls, from_=1, to=100, width=5); self.sp_qty.pack(side='left', padx=5)
        
        tk.Button(f_controls, text="Thêm", command=self._add_medicine).pack(side='left', padx=10)
        
        tk.Label(frame, text="Đơn thuốc hiện tại:", font=("Arial", 10)).pack(anchor='w', padx=5)
        self.lb_pres = tk.Listbox(frame, height=5); self.lb_pres.pack(fill='x', padx=5)
        
        tk.Button(frame, text="Xóa thuốc khỏi đơn", command=self._remove_medicine).pack(pady=5)
        
    def _add_medicine(self):
        name = self.cb_med.get(); qty = int(self.sp_qty.get())
        if not name: return
        
        if self.controller.check_stock(name, qty):
            self.exam_meds.append({'name': name, 'qty': qty})
            self._update_prescription_list()
            self.controller.update_prescription(self.current_exam_app_id, self.exam_meds)
        else:
            messagebox.showerror("Lỗi", f"Thuốc {name} không đủ tồn kho!")

    def _remove_medicine(self):
        sel = self.lb_pres.curselection()
        if sel:
            self.exam_meds.pop(sel[0])
            self._update_prescription_list()
            self.controller.update_prescription(self.current_exam_app_id, self.exam_meds)

    def _update_prescription_list(self):
        self.lb_pres.delete(0, tk.END)
        for item in self.exam_meds:
            self.lb_pres.insert(tk.END, f"{item['name']} x {item['qty']}")

    def _complete_examination(self):
        if not self.current_exam_app_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân để khám.")
            return
        
        diagnosis = self.txt_diag.get("1.0", tk.END).strip()
        if not diagnosis:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập chẩn đoán trước khi hoàn tất.")
            return

        if self.controller.finish_examination(
            self.current_exam_app_id, 
            diagnosis, 
            self.exam_meds, 
            self.exam_tests
        ):
            messagebox.showinfo("Thành công", "Đã hoàn tất khám và tạo hóa đơn!")
            self.lbl_status.config(text="Chưa chọn bệnh nhân", fg="black")
            self.load_appointments()
            self.current_exam_app_id = None
            self.exam_meds = []; self.exam_tests = []
            self.master_app.show_doctor_dashboard()
        else:
            messagebox.showerror("Lỗi", "Hoàn tất khám thất bại.")