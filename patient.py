"""
Patient module: quản lý bệnh nhân
- Xem hồ sơ sức khỏe (thông tin cơ bản + tiền sử)
- Chỉ định xét nghiệm (tạo lệnh xét nghiệm)
- Kê đơn thuốc (tạo đơn kê)
- Cập nhật kết quả khám/xét nghiệm

Sử dụng: Python 3.x, Tkinter, SQLite (file hospital.db)
Chạy: python patient_module.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "hospital.db"

# ------------------------- DATABASE INIT ---------------------------
def init_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Bảng bệnh nhân
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT,
            history TEXT
        )
    ''')

    # Bảng chỉ định xét nghiệm
    c.execute('''
        CREATE TABLE IF NOT EXISTS test_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            ordered_by_doctor INTEGER,
            tests TEXT, -- JSON-like comma separated list
            time TEXT,
            status TEXT, -- Pending / Completed
            results TEXT -- free text or JSON
        )
    ''')

    # Bảng kê đơn thuốc
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            prescribed_by_doctor INTEGER,
            meds TEXT, -- JSON-like comma separated list of med:dose:note
            time TEXT,
            note TEXT
        )
    ''')

    # Bảng kết quả khám/ghi chú khám
    c.execute('''
        CREATE TABLE IF NOT EXISTS visit_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            time TEXT,
            summary TEXT,
            vitals TEXT -- optional vitals
        )
    ''')

    conn.commit()
    conn.close()

# ------------------------- HÀM TIỆN ÍCH DB ---------------------------
def add_sample_patient(name, dob, gender, phone, address, history):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO patients (name,dob,gender,phone,address,history) VALUES (?,?,?,?,?,?)',
              (name, dob, gender, phone, address, history))
    conn.commit()
    conn.close()

# add test order
def add_test_order(patient_id, doctor_id, tests):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO test_orders (patient_id,ordered_by_doctor,tests,time,status,results) VALUES (?,?,?,?,?,?)',
              (patient_id, doctor_id, tests, time, 'Pending', ''))
    conn.commit()
    conn.close()

# add prescription
def add_prescription(patient_id, doctor_id, meds, note=''):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO prescriptions (patient_id,prescribed_by_doctor,meds,time,note) VALUES (?,?,?,?,?)',
              (patient_id, doctor_id, meds, time, note))
    conn.commit()
    conn.close()

# add visit result
def add_visit_result(patient_id, doctor_id, summary, vitals=''):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO visit_results (patient_id,doctor_id,time,summary,vitals) VALUES (?,?,?,?,?)',
              (patient_id, doctor_id, time, summary, vitals))
    conn.commit()
    conn.close()

# update test order results
def update_test_result(order_id, results_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE test_orders SET results=?, status=? WHERE id=?', (results_text, 'Completed', order_id))
    conn.commit()
    conn.close()

# ------------------------- UI: Patient Module ---------------------------
class PatientModule:
    def __init__(self, root, doctor_id=None):
        self.root = root
        self.doctor_id = doctor_id or 0
        self.root.title('Quản lý bệnh nhân')
        self.root.geometry('900x600')

        # Notebook tabs
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill='both', expand=True)

        # Tab: Danh sách bệnh nhân / Hồ sơ
        self.tab_patients = ttk.Frame(self.nb)
        self.nb.add(self.tab_patients, text='Hồ sơ & Danh sách')

        # Tab: Chỉ định xét nghiệm
        self.tab_tests = ttk.Frame(self.nb)
        self.nb.add(self.tab_tests, text='Chỉ định xét nghiệm')

        # Tab: Kê đơn thuốc
        self.tab_presc = ttk.Frame(self.nb)
        self.nb.add(self.tab_presc, text='Kê đơn thuốc')

        # Tab: Kết quả khám
        self.tab_results = ttk.Frame(self.nb)
        self.nb.add(self.tab_results, text='Kết quả khám')

        self.build_patients_tab()
        self.build_tests_tab()
        self.build_presc_tab()
        self.build_results_tab()

    # ----------------- Patients Tab -----------------
    def build_patients_tab(self):
        left = ttk.Frame(self.tab_patients)
        left.pack(side='left', fill='y', padx=8, pady=8)

        right = ttk.Frame(self.tab_patients)
        right.pack(side='right', fill='both', expand=True, padx=8, pady=8)

        # Search + add
        search_frame = ttk.Frame(left)
        search_frame.pack(fill='x', pady=4)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var).pack(side='left')
        tk.Button(search_frame, text='Tìm', command=self.search_patients).pack(side='left', padx=4)
        tk.Button(search_frame, text='Thêm bệnh nhân', command=self.open_add_patient).pack(side='left', padx=4)

        # Listbox patients
        self.patient_list = tk.Listbox(left, width=35)
        self.patient_list.pack(fill='y', expand=True)
        self.patient_list.bind('<<ListboxSelect>>', self.on_patient_select)

        # Patient details on right
        detail_lbl = ttk.Label(right, text='Hồ sơ bệnh nhân', font=('Helvetica', 14, 'bold'))
        detail_lbl.pack(anchor='nw')

        self.txt_profile = tk.Text(right, height=20)
        self.txt_profile.pack(fill='both', expand=True)

        # Buttons for actions
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill='x')
        tk.Button(btn_frame, text='Thêm chỉ định xét nghiệm', command=self.add_test_for_selected).pack(side='left', padx=4)
        tk.Button(btn_frame, text='Kê đơn thuốc cho bệnh nhân', command=self.prescribe_for_selected).pack(side='left', padx=4)
        tk.Button(btn_frame, text='Thêm kết quả khám', command=self.add_visit_result_for_selected).pack(side='left', padx=4)

        self.refresh_patient_list()

    def refresh_patient_list(self):
        self.patient_list.delete(0, tk.END)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, name, dob FROM patients ORDER BY name')
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.patient_list.insert(tk.END, f'{r[0]} - {r[1]} ({r[2]})')

    def search_patients(self):
        q = self.search_var.get().strip()
        self.patient_list.delete(0, tk.END)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, name, dob FROM patients WHERE name LIKE ? OR phone LIKE ?", (f'%{q}%', f'%{q}%'))
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.patient_list.insert(tk.END, f'{r[0]} - {r[1]} ({r[2]})')

    def on_patient_select(self, evt):
        sel = self.patient_list.curselection()
        if not sel:
            return
        text = self.patient_list.get(sel[0])
        patient_id = int(text.split(' - ')[0])
        self.show_patient_profile(patient_id)

    def show_patient_profile(self, patient_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT name,dob,gender,phone,address,history FROM patients WHERE id=?', (patient_id,))
        row = c.fetchone()
        conn.close()
        self.txt_profile.delete('1.0', tk.END)
        if row:
            name, dob, gender, phone, address, history = row
            out = f"Tên: {name}\nNgày sinh: {dob}\nGiới tính: {gender}\nPhone: {phone}\nĐịa chỉ: {address}\n\nTiền sử:\n{history}\n"
            # show recent tests and prescriptions
            out += '\n--- Lịch sử xét nghiệm ---\n'
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('SELECT id,tests,time,status,results FROM test_orders WHERE patient_id=? ORDER BY time DESC LIMIT 5', (patient_id,))
            for r in c.fetchall():
                out += f'#{r[0]} {r[3]} @ {r[2]}: {r[1]}\n  KQ: {r[4]}\n'

            out += '\n--- Lịch sử kê đơn ---\n'
            c.execute('SELECT id,meds,time,note FROM prescriptions WHERE patient_id=? ORDER BY time DESC LIMIT 5', (patient_id,))
            for r in c.fetchall():
                out += f'#{r[0]} @ {r[2]}: {r[1]}\n  Ghi chú: {r[3]}\n'
            conn.close()

            self.txt_profile.insert(tk.END, out)

    def open_add_patient(self):
        win = tk.Toplevel(self.root)
        win.title('Thêm bệnh nhân')
        labels = ['Tên', 'Ngày sinh (YYYY-MM-DD)', 'Giới tính', 'Phone', 'Địa chỉ', 'Tiền sử']
        entries = []
        for l in labels:
            ttk.Label(win, text=l).pack(anchor='w')
            e = tk.Entry(win, width=50)
            e.pack(fill='x', padx=4, pady=2)
            entries.append(e)
        def save():
            vals = [e.get().strip() for e in entries]
            if not vals[0]:
                messagebox.showwarning('Lỗi', 'Tên không được để trống')
                return
            add_sample_patient(*vals)
            messagebox.showinfo('Thành công', 'Đã thêm bệnh nhân')
            win.destroy()
            self.refresh_patient_list()
        tk.Button(win, text='Lưu', command=save).pack(pady=6)

    # ----------------- Tests Tab -----------------
    def build_tests_tab(self):
        top = ttk.Frame(self.tab_tests)
        top.pack(fill='x', padx=6, pady=6)
        tk.Button(top, text='Tải lại', command=self.refresh_test_list).pack(side='left')

        mid = ttk.Frame(self.tab_tests)
        mid.pack(fill='both', expand=True, padx=6, pady=6)

        # Left: List of test orders
        left = ttk.Frame(mid)
        left.pack(side='left', fill='y')
        self.test_tree = ttk.Treeview(left, columns=('id','patient','tests','time','status'), show='headings')
        for col in ('id','patient','tests','time','status'):
            self.test_tree.heading(col, text=col)
        self.test_tree.pack(fill='y', expand=True)
        self.test_tree.bind('<<TreeviewSelect>>', self.on_test_select)

        # Right: details and update
        right = ttk.Frame(mid)
        right.pack(side='right', fill='both', expand=True)
        ttk.Label(right, text='Chi tiết lệnh xét nghiệm', font=('Helvetica',12,'bold')).pack(anchor='nw')
        self.txt_test_detail = tk.Text(right, height=15)
        self.txt_test_detail.pack(fill='both', expand=True)
        tk.Button(right, text='Cập nhật kết quả', command=self.update_selected_test_result).pack(pady=4)

        self.refresh_test_list()

    def refresh_test_list(self):
        for i in self.test_tree.get_children():
            self.test_tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT t.id, p.name, t.tests, t.time, t.status FROM test_orders t LEFT JOIN patients p ON p.id=t.patient_id ORDER BY t.time DESC')
        for r in c.fetchall():
            self.test_tree.insert('', tk.END, values=r)
        conn.close()

    def on_test_select(self, evt):
        sel = self.test_tree.selection()
        if not sel: return
        vals = self.test_tree.item(sel[0])['values']
        order_id = vals[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT tests,time,status,results,patient_id FROM test_orders WHERE id=?', (order_id,))
        r = c.fetchone()
        conn.close()
        if r:
            tests, time, status, results, pid = r
            out = f'Order #{order_id} for patient #{pid}\nTests: {tests}\nTime: {time}\nStatus: {status}\n\nResults:\n{results}\n'
            self.txt_test_detail.delete('1.0', tk.END)
            self.txt_test_detail.insert(tk.END, out)

    def update_selected_test_result(self):
        sel = self.test_tree.selection()
        if not sel:
            messagebox.showwarning('Chú ý', 'Chọn một lệnh xét nghiệm')
            return
        order_id = self.test_tree.item(sel[0])['values'][0]
        # open dialog to input results
        win = tk.Toplevel(self.root)
        win.title(f'Cập nhật kết quả cho lệnh #{order_id}')
        tk.Label(win, text='Kết quả (text)').pack(anchor='w')
        txt = tk.Text(win, height=10)
        txt.pack(fill='both', expand=True)
        def save():
            res = txt.get('1.0', tk.END).strip()
            if not res:
                messagebox.showwarning('Lỗi','Kết quả rỗng')
                return
            update_test_result(order_id, res)
            messagebox.showinfo('OK','Đã lưu kết quả')
            win.destroy()
            self.refresh_test_list()
        tk.Button(win, text='Lưu', command=save).pack(pady=6)

    def add_test_for_selected(self):
        sel = self.patient_list.curselection()
        if not sel:
            messagebox.showwarning('Chú ý', 'Chọn bệnh nhân trong tab Hồ sơ trước')
            return
        patient_id = int(self.patient_list.get(sel[0]).split(' - ')[0])
        # dialog to input tests
        win = tk.Toplevel(self.root)
        win.title('Chỉ định xét nghiệm')
        tk.Label(win, text='Danh sách xét nghiệm (ngăn cách bằng dấu phẩy)').pack(anchor='w')
        e = tk.Entry(win, width=80)
        e.pack(fill='x', padx=6, pady=6)
        def save():
            tests = e.get().strip()
            if not tests:
                messagebox.showwarning('Lỗi','Nhập ít nhất 1 xét nghiệm')
                return
            add_test_order(patient_id, self.doctor_id, tests)
            messagebox.showinfo('OK','Đã tạo lệnh xét nghiệm')
            win.destroy()
            self.refresh_test_list()
        tk.Button(win, text='Gửi', command=save).pack(pady=6)

    # ----------------- Prescriptions Tab -----------------
    def build_presc_tab(self):
        top = ttk.Frame(self.tab_presc)
        top.pack(fill='x', padx=6, pady=6)
        tk.Button(top, text='Tải lại', command=self.refresh_presc_list).pack(side='left')

        mid = ttk.Frame(self.tab_presc)
        mid.pack(fill='both', expand=True, padx=6, pady=6)

        left = ttk.Frame(mid)
        left.pack(side='left', fill='y')
        self.pres_tree = ttk.Treeview(left, columns=('id','patient','meds','time'), show='headings')
        for col in ('id','patient','meds','time'):
            self.pres_tree.heading(col, text=col)
        self.pres_tree.pack(fill='y', expand=True)
        self.pres_tree.bind('<<TreeviewSelect>>', self.on_pres_select)

        right = ttk.Frame(mid)
        right.pack(side='right', fill='both', expand=True)
        ttk.Label(right, text='Chi tiết đơn thuốc', font=('Helvetica',12,'bold')).pack(anchor='nw')
        self.txt_presc_detail = tk.Text(right, height=15)
        self.txt_presc_detail.pack(fill='both', expand=True)

        self.refresh_presc_list()

    def refresh_presc_list(self):
        for i in self.pres_tree.get_children():
            self.pres_tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT r.id, p.name, r.meds, r.time FROM prescriptions r LEFT JOIN patients p ON p.id=r.patient_id ORDER BY r.time DESC')
        for r in c.fetchall():
            self.pres_tree.insert('', tk.END, values=r)
        conn.close()

    def on_pres_select(self, evt):
        sel = self.pres_tree.selection()
        if not sel: return
        vals = self.pres_tree.item(sel[0])['values']
        pres_id = vals[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT meds,time,note,patient_id FROM prescriptions WHERE id=?', (pres_id,))
        r = c.fetchone()
        conn.close()
        if r:
            meds, time, note, pid = r
            out = f'Prescription #{pres_id} for patient #{pid}\nTime: {time}\nMeds: {meds}\nNote: {note}\n'
            self.txt_presc_detail.delete('1.0', tk.END)
            self.txt_presc_detail.insert(tk.END, out)

    def prescribe_for_selected(self):
        sel = self.patient_list.curselection()
        if not sel:
            messagebox.showwarning('Chú ý', 'Chọn bệnh nhân trong tab Hồ sơ trước')
            return
        patient_id = int(self.patient_list.get(sel[0]).split(' - ')[0])
        win = tk.Toplevel(self.root)
        win.title('Kê đơn thuốc')
        tk.Label(win, text='Danh sách thuốc (format: tên:liều lượng:số_ngày, ngăn cách bằng dấu phẩy)').pack(anchor='w')
        e = tk.Entry(win, width=100)
        e.pack(fill='x', padx=6, pady=6)
        tk.Label(win, text='Ghi chú / chỉ định thêm').pack(anchor='w')
        note = tk.Entry(win, width=100)
        note.pack(fill='x', padx=6, pady=6)
        def save():
            meds = e.get().strip()
            n = note.get().strip()
            if not meds:
                messagebox.showwarning('Lỗi','Nhập thuốc')
                return
            add_prescription(patient_id, self.doctor_id, meds, n)
            messagebox.showinfo('OK','Đã lưu đơn thuốc')
            win.destroy()
            self.refresh_presc_list()
        tk.Button(win, text='Lưu', command=save).pack(pady=6)

    # ----------------- Visit Results Tab -----------------
    def build_results_tab(self):
        top = ttk.Frame(self.tab_results)
        top.pack(fill='x', padx=6, pady=6)
        tk.Button(top, text='Tải lại', command=self.refresh_visit_list).pack(side='left')

        mid = ttk.Frame(self.tab_results)
        mid.pack(fill='both', expand=True, padx=6, pady=6)

        left = ttk.Frame(mid)
        left.pack(side='left', fill='y')
        self.visit_tree = ttk.Treeview(left, columns=('id','patient','time'), show='headings')
        for col in ('id','patient','time'):
            self.visit_tree.heading(col, text=col)
        self.visit_tree.pack(fill='y', expand=True)
        self.visit_tree.bind('<<TreeviewSelect>>', self.on_visit_select)

        right = ttk.Frame(mid)
        right.pack(side='right', fill='both', expand=True)
        ttk.Label(right, text='Chi tiết kết quả khám', font=('Helvetica',12,'bold')).pack(anchor='nw')
        self.txt_visit_detail = tk.Text(right, height=20)
        self.txt_visit_detail.pack(fill='both', expand=True)

        self.refresh_visit_list()

    def refresh_visit_list(self):
        for i in self.visit_tree.get_children():
            self.visit_tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT v.id, p.name, v.time FROM visit_results v LEFT JOIN patients p ON p.id=v.patient_id ORDER BY v.time DESC')
        for r in c.fetchall():
            self.visit_tree.insert('', tk.END, values=r)
        conn.close()

    def on_visit_select(self, evt):
        sel = self.visit_tree.selection()
        if not sel: return
        vals = self.visit_tree.item(sel[0])['values']
        vid = vals[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT summary,vitals,doctor_id,time,patient_id FROM visit_results WHERE id=?', (vid,))
        r = c.fetchone()
        conn.close()
        if r:
            summary, vitals, docid, time, pid = r
            out = f'Visit #{vid} for patient #{pid} by doctor #{docid} @ {time}\n\nSummary:\n{summary}\n\nVitals:\n{vitals}\n'
            self.txt_visit_detail.delete('1.0', tk.END)
            self.txt_visit_detail.insert(tk.END, out)

    def add_visit_result_for_selected(self):
        sel = self.patient_list.curselection()
        if not sel:
            messagebox.showwarning('Chú ý', 'Chọn bệnh nhân')
            return
        patient_id = int(self.patient_list.get(sel[0]).split(' - ')[0])
        win = tk.Toplevel(self.root)
        win.title('Thêm kết quả khám / ghi chú')
        tk.Label(win, text='Tóm tắt kết quả / chẩn đoán').pack(anchor='w')
        txt = tk.Text(win, height=8)
        txt.pack(fill='both', expand=True, padx=6, pady=6)
        tk.Label(win, text='Vitals (ví dụ: BP:120/80; HR:78)').pack(anchor='w')
        vit = tk.Entry(win, width=80)
        vit.pack(fill='x', padx=6, pady=6)
        def save():
            s = txt.get('1.0', tk.END).strip()
            v = vit.get().strip()
            if not s:
                messagebox.showwarning('Lỗi','Nhập tóm tắt')
                return
            add_visit_result(patient_id, self.doctor_id, s, v)
            messagebox.showinfo('OK','Đã lưu kết quả khám')
            win.destroy()
            self.refresh_visit_list()
        tk.Button(win, text='Lưu', command=save).pack(pady=6)

# ------------------------- RUN APP ---------------------------
if __name__ == '__main__':
    init_database()
    # Thêm dữ liệu mẫu nếu chưa có
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM patients')
    cnt = c.fetchone()[0]
    conn.close()
    if cnt == 0:
        add_sample_patient('Nguyen Van A','1990-01-01','Nam','0123456789','Hanoi','Tiền sử: dị ứng penicillin')
        add_sample_patient('Tran Thi B','1985-05-12','Nữ','0987654321','HCM','Tiền sử: tăng huyết áp')

    root = tk.Tk()
    app = PatientModule(root, doctor_id=1)
    root.mainloop()
