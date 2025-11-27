import tkinter as tk
from tkinter import ttk, messagebox
import time

class PaymentView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.total_amount = 0
        self.selected_items = []
        self.all_invoices = [] # Lưu trữ toàn bộ hóa đơn để lọc
        
        # Tiêu đề
        ttk.Label(self, text="THANH TOÁN VIỆN PHÍ", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Layout chia làm 2 cột
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20)
        
        # --- CỘT PHẢI (Thông tin thanh toán) ---
        right_frame = ttk.LabelFrame(content_frame, text="Thông tin thanh toán", padding=15, width=300)
        right_frame.pack(side="right", fill="y", expand=False)
        right_frame.pack_propagate(False) 
        
        # --- CỘT TRÁI (Danh sách hóa đơn) ---
        left_frame = ttk.LabelFrame(content_frame, text="Lịch sử giao dịch", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # === BỘ LỌC (MỚI THÊM) ===
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(filter_frame, text="Lọc trạng thái:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Tất cả")
        self.cb_filter = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly", width=20)
        self.cb_filter['values'] = ["Tất cả", "Chưa thanh toán", "Đã thanh toán"]
        self.cb_filter.pack(side="left")
        self.cb_filter.bind("<<ComboboxSelected>>", self.apply_filter) # Sự kiện khi chọn
        
        # Treeview
        columns = ("id", "service", "date", "amount", "status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("service", text="Dịch vụ / Thuốc")
        self.tree.heading("date", text="Ngày tạo")
        self.tree.heading("amount", text="Số tiền")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=30)
        self.tree.column("service", width=200)
        self.tree.column("date", width=120)
        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("status", width=100, anchor="center")
        
        # Màu sắc
        self.tree.tag_configure("unpaid", foreground="red")
        self.tree.tag_configure("paid", foreground="green")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        ttk.Label(left_frame, text="* Giữ phím Ctrl để chọn nhiều hóa đơn cần thanh toán", font=("Arial", 9, "italic"), foreground="gray").pack(pady=5, anchor="w")

        # --- NỘI DUNG CỘT PHẢI ---
        ttk.Label(right_frame, text="Tổng thanh toán:", font=("Arial", 10)).pack(anchor="w")
        self.lbl_total = ttk.Label(right_frame, text="0 VNĐ", font=("Arial", 18, "bold"), foreground="#d9534f")
        self.lbl_total.pack(anchor="w", pady=(0, 20))
        
        ttk.Label(right_frame, text="Phương thức thanh toán:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        
        self.method_var = tk.StringVar(value="qrcode")
        methods = [("Quét mã QR (Momo/Banking)", "qrcode"), ("Thẻ ATM / Visa / Master", "card"), ("Thẻ BHYT (Đồng chi trả)", "insurance")]
        for text, val in methods:
            ttk.Radiobutton(right_frame, text=text, variable=self.method_var, value=val).pack(anchor="w", pady=2)

        self.qr_frame = tk.Frame(right_frame, bg="white", width=150, height=150, highlightbackground="gray", highlightthickness=1)
        self.qr_frame.pack(pady=20); self.qr_frame.pack_propagate(False)
        ttk.Label(self.qr_frame, text="[Mô phỏng QR Code]", background="white").place(relx=0.5, rely=0.5, anchor="center")

        self.btn_pay = ttk.Button(right_frame, text="XÁC NHẬN THANH TOÁN", command=self.process_payment, state="disabled")
        self.btn_pay.pack(fill="x", pady=10)

        self.fetch_invoices()

    def fetch_invoices(self):
        """Lấy dữ liệu từ DB và lưu vào biến tạm"""
        self.all_invoices = self.controller.db.get_all_patient_invoices(self.controller.auth.current_user)
        # Sắp xếp mặc định: Chưa thanh toán lên đầu
        self.all_invoices.sort(key=lambda x: 0 if x['status'] == 'Unpaid' else 1)
        self.apply_filter()

    def apply_filter(self, event=None):
        """Hiển thị dữ liệu lên bảng dựa theo bộ lọc"""
        # 1. Xóa bảng cũ
        for item in self.tree.get_children(): self.tree.delete(item)
        
        # 2. Lấy điều kiện lọc
        filter_type = self.filter_var.get() # "Tất cả", "Chưa thanh toán", ...
        
        # 3. Duyệt và lọc
        for inv in self.all_invoices:
            status_code = inv['status'] # Unpaid, Paid
            
            # Logic lọc
            if filter_type == "Chưa thanh toán" and status_code != "Unpaid": continue
            if filter_type == "Đã thanh toán" and status_code != "Paid": continue
            
            # Hiển thị
            status_text = "Chưa thanh toán" if status_code == 'Unpaid' else "Đã thanh toán"
            tag = "unpaid" if status_code == 'Unpaid' else "paid"
            amount_str = "{:,.0f} đ".format(inv['amount'])
            
            self.tree.insert("", "end", 
                             values=(inv['id'], inv['service'], inv['date'], amount_str, status_text), 
                             tags=(tag, str(inv['amount']), inv['status']))

    def on_select(self, event):
        selected_items = self.tree.selection()
        total = 0
        self.selected_items = []
        
        for item_id in selected_items:
            tags = self.tree.item(item_id, "tags")
            status_raw = tags[2]
            
            # Chỉ cho phép thanh toán nếu chưa trả
            if status_raw == 'Unpaid':
                raw_amount = int(tags[1]) 
                invoice_db_id = self.tree.item(item_id, "values")[0]
                total += raw_amount
                self.selected_items.append(invoice_db_id)
            
        self.total_amount = total
        self.lbl_total.config(text=f"{total:,.0f} VNĐ")
        
        if total > 0:
            self.btn_pay.config(state="normal", text=f"THANH TOÁN ({len(self.selected_items)})")
        else:
            self.btn_pay.config(state="disabled", text="XÁC NHẬN THANH TOÁN")

    def process_payment(self):
        if not self.selected_items: return
        method = self.method_var.get()
        method_name = "Ví điện tử/QR" if method == "qrcode" else ("Thẻ ngân hàng" if method == "card" else "Bảo hiểm y tế")
        PaymentProcessingPopup(self, self.total_amount, method_name, self.finish_payment)

    def finish_payment(self):
        for invoice_id in self.selected_items:
            self.controller.db.pay_invoice(invoice_id)
        messagebox.showinfo("Thành công", "Giao dịch thành công!")
        
        # Reset giao diện (Load lại dữ liệu mới nhất)
        self.fetch_invoices()
        self.lbl_total.config(text="0 VNĐ")
        self.btn_pay.config(state="disabled")

class PaymentProcessingPopup(tk.Toplevel):
    def __init__(self, parent, amount, method, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Đang xử lý...")
        self.geometry("300x150")
        x = parent.winfo_rootx() + 150; y = parent.winfo_rooty() + 150
        self.geometry(f"+{x}+{y}"); self.grab_set()
        
        ttk.Label(self, text=f"Đang kết nối cổng thanh toán...", font=("Arial", 10)).pack(pady=10)
        ttk.Label(self, text=f"Số tiền: {amount:,.0f} VNĐ", font=("Arial", 11, "bold")).pack(pady=5)
        ttk.Label(self, text=f"Qua: {method}", font=("Arial", 9)).pack()
        
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill="x", padx=20, pady=15); self.progress.start(10)
        self.after(2000, self.complete)

    def complete(self):
        self.destroy(); self.callback()