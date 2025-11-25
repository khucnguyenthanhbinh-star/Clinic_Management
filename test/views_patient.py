import tkinter as tk
from tkinter import ttk, messagebox
import json

class PatientViewManager:
    def __init__(self, master_app, controller, patient_id):
        self.master_app = master_app
        self.controller = controller
        self.current_user_id = patient_id
        self.appt_tree_patient = None
        self.booking_state = {}

    def load_appointments_to_tree(self, tree):
        tree.delete(*tree.get_children())
        self.controller.cursor.execute("SELECT A.id, A.date, A.time, D.full_name, A.status FROM Appointments A JOIN Doctors D ON A.doctor_id = D.user_id WHERE A.patient_id=? ORDER BY A.date DESC, A.time DESC", (self.current_user_id,))
        for row in self.controller.cursor.fetchall():
            tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3], row[4]))
        
    def build_patient_info_tab(self, frame):
        info = self.controller.get_patient_info(self.current_user_id)
        tk.Label(frame, text="CẬP NHẬT THÔNG TIN", font=("bold")).pack(pady=10)
        
        tk.Label(frame, text="Ngày sinh (DD/MM/YYYY):").pack()
        dob_entry = tk.Entry(frame); dob_entry.insert(0, info[4] if info[4] else ""); dob_entry.pack()
        tk.Label(frame, text="Địa chỉ:").pack()
        addr_entry = tk.Entry(frame); addr_entry.insert(0, info[5] if info[5] else ""); addr_entry.pack()
        tk.Label(frame, text="Tiền sử bệnh:").pack()
        hist_entry = tk.Entry(frame); hist_entry.insert(0, info[6] if info[6] else ""); hist_entry.pack()

        def save():
            self.controller.update_patient_info(self.current_user_id, dob_entry.get(), addr_entry.get(), hist_entry.get())
            messagebox.showinfo("OK", "Đã cập nhật!")
        tk.Button(frame, text="Lưu", command=save).pack(pady=10)

    def build_patient_appt_tab(self, frame):
        tk.Label(frame, text="Lịch hẹn của tôi").pack()
        tree = ttk.Treeview(frame, columns=("Date", "Time", "Doc", "Status"), show="headings", height=5)
        tree.heading("Date", text="Ngày"); tree.heading("Time", text="Giờ"); tree.heading("Doc", text="Bác sĩ"); tree.heading("Status", text="Trạng thái")
        tree.pack(fill='x')
        self.appt_tree_patient = tree
        self.load_appointments_to_tree(tree)
        
        def cancel():
            selected_item = tree.focus()
            if not selected_item: messagebox.showerror("Lỗi", "Vui lòng chọn một lịch hẹn."); return
            app_id = int(selected_item)
            status = tree.item(selected_item)['values'][3]
            if status != 'Pending': messagebox.showerror("Lỗi", f"Không thể hủy lịch {status}"); return
            if messagebox.askyesno("Xác nhận", "Hủy lịch hẹn này?"):
                if self.controller.cancel_appointment(app_id):
                    messagebox.showinfo("Thành công", "Đã hủy."); self.load_appointments_to_tree(tree)

        tk.Button(frame, text="Hủy Lịch Hẹn", command=cancel).pack(pady=5)
        
        tk.Label(frame, text="--- ĐẶT LỊCH MỚI ---", font="bold").pack(pady=10)
        tk.Label(frame, text="B1: Chọn Loại khám").pack()
        type_var = tk.StringVar()
        cb_type = ttk.Combobox(frame, textvariable=type_var, values=["Chuyên khoa 1", "Chuyên khoa 2", "Chuyên khoa 3"]); cb_type.pack()
        tk.Label(frame, text="Mô tả triệu chứng:").pack(); e_symp = tk.Entry(frame); e_symp.pack()

        frame_step2 = tk.Frame(frame); frame_step2.pack()
        frame_step4 = tk.Frame(frame); frame_step4.pack()

        def step2_show_doctors():
            spec = type_var.get()
            self.booking_state = {'reason': spec, 'symptoms': e_symp.get()}
            docs = self.controller.get_doctors_by_type(spec)
            for w in frame_step2.winfo_children(): w.destroy()
            
            tk.Label(frame_step2, text="B2 & B3: Chọn Bác sĩ").pack()
            lb_docs = tk.Listbox(frame_step2, height=3)
            docs_map = {}
            for d in docs: lb_docs.insert(tk.END, d[1]); docs_map[d[1]] = d[0]
            lb_docs.pack()

            def step4_show_slots():
                sel = lb_docs.curselection()
                if not sel: return
                doc_id = docs_map[lb_docs.get(sel[0])]
                self.booking_state['doc_id'] = doc_id
                slots = self.controller.get_all_doctor_slots(doc_id)
                for w in frame_step4.winfo_children(): w.destroy()
                
                tk.Label(frame_step4, text="B4: Chọn Slot").pack()
                cb_slots = ttk.Combobox(frame_step4, values=[f"{s[0]} | {s[1]}" for s in slots]); cb_slots.pack()
                
                def step5_confirm():
                    val = cb_slots.get()
                    if not val: return
                    date, time = val.split(" | ")
                    self.controller.book_appointment(self.current_user_id, self.booking_state['doc_id'], date, time, self.booking_state['reason'], self.booking_state['symptoms'])
                    messagebox.showinfo("Thành công", "Đã đặt lịch!"); self.load_appointments_to_tree(tree); cb_slots.set('')

                tk.Button(frame_step4, text="B5: Xác nhận", command=step5_confirm).pack()
            tk.Button(frame_step2, text="Chọn Bác sĩ này", command=step4_show_slots).pack()
        tk.Button(frame, text="Tìm Bác sĩ", command=step2_show_doctors).pack()

    def build_patient_records_tab(self, frame):
        cols = ("Date", "Doc", "Diagnosis", "Results", "Meds")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)
        records = self.controller.get_patient_records(self.current_user_id)
        for r in records:
            res_str = ", ".join([t['name'] for t in json.loads(r[3])]) if r[3] else ""
            med_str = ", ".join([m['name'] for m in json.loads(r[4])]) if r[4] else ""
            tree.insert("", "end", values=(r[0], r[1], r[2] or "Đang khám", res_str, med_str))

    def build_patient_payment_tab(self, frame):
        tree = ttk.Treeview(frame, columns=("ID", "Amount", "Date"), show="headings", height=5)
        tree.heading("ID", text="ID"); tree.heading("Amount", text="Số tiền"); tree.heading("Date", text="Ngày")
        tree.pack()
        invoices = self.controller.get_unpaid_invoices(self.current_user_id)
        for inv in invoices: tree.insert("", "end", values=inv)

        def pay_online():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0]); inv_id = item['values'][0]
            if messagebox.askyesno("Thanh toán", f"Thanh toán hóa đơn {inv_id}?"):
                self.controller.pay_invoice(inv_id); messagebox.showinfo("OK", "Đã thanh toán!"); tree.delete(sel[0])
        tk.Button(frame, text="Thanh toán Online", command=pay_online).pack(pady=10)

    def build_notif_tab(self, frame):
        lb = tk.Listbox(frame); lb.pack(fill='both', expand=True)
        self.controller.cursor.execute("SELECT message, created_at FROM Notifications WHERE user_id=? ORDER BY id DESC", (self.current_user_id,))
        for row in self.controller.cursor.fetchall(): lb.insert(tk.END, f"[{row[1]}] {row[0]}")