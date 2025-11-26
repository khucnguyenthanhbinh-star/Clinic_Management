import tkinter as tk
from tkinter import ttk, messagebox

class ManageInvoicesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ HÓA ĐƠN", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(filter_frame, text="Lọc trạng thái:").pack(side="left", padx=5)
        self.status_combo = ttk.Combobox(filter_frame, values=["Tất cả", "Paid", "Unpaid"], state="readonly", width=15)
        self.status_combo.set("Tất cả")
        self.status_combo.pack(side="left", padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_invoices())
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Đánh dấu đã trả", command=self.mark_as_paid).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Đánh dấu chưa trả", command=self.mark_as_unpaid).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("id", "patient", "service", "amount", "status", "date"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("id", text="ID")
        self.tree.heading("patient", text="Bệnh nhân")
        self.tree.heading("service", text="Dịch vụ")
        self.tree.heading("amount", text="Số tiền")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("date", text="Ngày tạo")
        
        self.tree.column("id", width=40)
        self.tree.column("patient", width=120)
        self.tree.column("service", width=150)
        self.tree.column("amount", width=100)
        self.tree.column("status", width=80)
        self.tree.column("date", width=100)
        self.tree.pack(fill="both", expand=True)
        
        self.invoices = []
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.invoices = self.controller.db.get_all_invoices()
        for inv in self.invoices:
            self.tree.insert("", "end", values=(
                inv["id"], inv["patient"], inv["service"], f"{inv['amount']:,} đ", inv["status"], inv["date"]
            ), tags=(inv["id"],))

    def filter_invoices(self):
        status_filter = self.status_combo.get()
        self.tree.delete(*self.tree.get_children())
        
        for inv in self.invoices:
            if status_filter == "Tất cả" or inv["status"] == status_filter:
                self.tree.insert("", "end", values=(
                    inv["id"], inv["patient"], inv["service"], f"{inv['amount']:,} đ", inv["status"], inv["date"]
                ), tags=(inv["id"],))

    def mark_as_paid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn")
            return
        
        item = self.tree.item(selected[0])
        invoice_id = item["values"][0]
        
        self.controller.db.update_invoice_status(invoice_id, "Paid")
        messagebox.showinfo("Thành công", "Đã cập nhật trạng thái")
        self.refresh_tree()

    def mark_as_unpaid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn")
            return
        
        item = self.tree.item(selected[0])
        invoice_id = item["values"][0]
        
        self.controller.db.update_invoice_status(invoice_id, "Unpaid")
        messagebox.showinfo("Thành công", "Đã cập nhật trạng thái")
        self.refresh_tree()
