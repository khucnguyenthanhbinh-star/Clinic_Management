import tkinter as tk
from tkinter import ttk, messagebox

class ManageMedicinesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="QUẢN LÝ KHO THUỐC", font=("Arial", 16, "bold")).pack(pady=20)

        # === NOTEBOOK (TAB) ===
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Quản lý kho thuốc
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Quản lý Kho")
        self.setup_inventory_tab()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

      

    def setup_inventory_tab(self):
        """Thiết lập tab quản lý kho thuốc"""
        # === FORM NHẬP/XUẤT THUỐC ===
        form_frame = ttk.LabelFrame(self.inventory_frame, text="Nhập/Xuất thuốc", padding=10)
        form_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(form_frame, text="Tên thuốc:").grid(row=0, column=0, pady=5, sticky="e")
        self.medicine_entry = ttk.Entry(form_frame, width=25)
        self.medicine_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Số lượng:").grid(row=1, column=0, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(form_frame, width=25)
        self.quantity_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Đơn vị:").grid(row=2, column=0, pady=5, sticky="e")
        self.unit_entry = ttk.Entry(form_frame, width=25)
        self.unit_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Giá (VNĐ):").grid(row=3, column=0, pady=5, sticky="e")
        self.price_entry = ttk.Entry(form_frame, width=25)
        self.price_entry.grid(row=3, column=1, pady=5, padx=5)

        btn_frame_form = ttk.Frame(form_frame)
        btn_frame_form.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame_form, text="Nhập kho", command=self.add_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame_form, text="Xuất kho", command=self.subtract_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame_form, text="Làm mới", command=self.refresh_tree).pack(side="left", padx=5)

        # === SEARCH BAR ===
        search_frame = ttk.Frame(self.inventory_frame)
        search_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_medicines())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)

        # === TREEVIEW ===
        self.tree = ttk.Treeview(self.inventory_frame, columns=("medicine", "quantity", "unit", "price"), show="headings", height=12)
        self.tree.heading("medicine", text="Tên thuốc")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.heading("unit", text="Đơn vị")
        self.tree.heading("price", text="Giá (VNĐ)")

        self.tree.column("medicine", width=250)
        self.tree.column("quantity", width=100)
        self.tree.column("unit", width=100)
        self.tree.column("price", width=120)

        scrollbar = ttk.Scrollbar(self.inventory_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)

        # === BUTTON FRAME ===
        btn_frame = ttk.Frame(self.inventory_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        ttk.Button(btn_frame, text="Chỉnh sửa", command=self.edit_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_medicine).pack(side="left", padx=5)

        self.all_medicines = {}
        self.refresh_tree()

    def setup_revenue_tab(self):
        """Thiết lập tab xem doanh thu bán thuốc"""
        tk.Label(self.revenue_frame, text="DOANH THU BÁN THUỐC", font=("Arial", 14, "bold")).pack(pady=15)

        # === TREEVIEW DOANH THU ===
        self.revenue_tree = ttk.Treeview(self.revenue_frame, columns=("medicine", "sold_qty", "price", "total_revenue"), show="headings", height=15)
        self.revenue_tree.heading("medicine", text="Tên thuốc")
        self.revenue_tree.heading("sold_qty", text="Số lượng đã bán")
        self.revenue_tree.heading("price", text="Giá/Đơn vị (VNĐ)")
        self.revenue_tree.heading("total_revenue", text="Tổng Doanh Thu (VNĐ)")

        self.revenue_tree.column("medicine", width=250)
        self.revenue_tree.column("sold_qty", width=130)
        self.revenue_tree.column("price", width=130)
        self.revenue_tree.column("total_revenue", width=150)

        scrollbar_revenue = ttk.Scrollbar(self.revenue_frame, orient="vertical", command=self.revenue_tree.yview)
        self.revenue_tree.configure(yscroll=scrollbar_revenue.set)

        self.revenue_tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar_revenue.pack(side="right", fill="y", padx=(0, 20), pady=10)

        # === BUTTON REFRESH REVENUE ===
        btn_frame_revenue = ttk.Frame(self.revenue_frame)
        btn_frame_revenue.pack(fill="x", padx=20, pady=10)
        ttk.Button(btn_frame_revenue, text="Cập nhật Doanh Thu", command=self.refresh_revenue).pack(side="left", padx=5)

        # === SUMMARY FRAME ===
        summary_frame = ttk.LabelFrame(self.revenue_frame, text="Tổng Hợp", padding=10)
        summary_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(summary_frame, text="Tổng doanh thu tất cả thuốc:", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.total_revenue_label = tk.Label(summary_frame, text="0 VNĐ", font=("Arial", 10))
        self.total_revenue_label.pack(side="left", padx=5)

        self.refresh_revenue()

    def refresh_tree(self):
        """Làm mới danh sách thuốc"""
        self.all_medicines = self.controller.db.get_medicines()
        self.filter_medicines()

    def filter_medicines(self):
        """Lọc thuốc theo tìm kiếm"""
        search_term = self.search_var.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)
        medicines = self.controller.db.get_medicines()

        for name, info in medicines.items():
            if search_term in name.lower():
                price = info.get("price", 0)
                self.tree.insert("", "end", values=(name, info["quantity"], info["unit"], f"{price:,} VNĐ"))

    def refresh_revenue(self):
        """Cập nhật doanh thu bán thuốc"""
        for item in self.revenue_tree.get_children():
            self.revenue_tree.delete(item)

        # Lấy dữ liệu doanh thu từ database
        revenue_data = self.controller.db.get_medicine_sales_revenue()
        
        total_revenue = 0
        for med_name, sold_qty, price, med_revenue in revenue_data:
            self.revenue_tree.insert("", "end", values=(med_name, sold_qty, f"{price:,} VNĐ", f"{med_revenue:,} VNĐ"))
            total_revenue += med_revenue

        # Cập nhật tổng doanh thu
        self.total_revenue_label.config(text=f"{total_revenue:,} VNĐ")

    def on_tab_change(self, event):
        """Refresh data khi tab được chọn"""
        selected_tab = self.notebook.select()
        if selected_tab == str(self.notebook.tabs()[0]):
            self.refresh_tree()
        elif selected_tab == str(self.notebook.tabs()[1]):
            self.refresh_revenue()

    def get_selected_medicine(self):
        """Lấy thuốc được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một loại thuốc")
            return None
        return selection[0]

    def add_medicine(self):
        """Thêm thuốc vào kho"""
        name = self.medicine_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        unit = self.unit_entry.get().strip()
        price = self.price_entry.get().strip()

        if not name or not quantity or not unit or not price:
            messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin")
            return

        try:
            qty = int(quantity)
            price_int = int(price)
            if qty <= 0 or price_int < 0:
                messagebox.showwarning("Thông báo", "Số lượng phải lớn hơn 0 và giá không được âm")
                return

            self.controller.db.add_medicine(name, qty, unit, price_int)
            messagebox.showinfo("Thành công", "Đã cập nhật kho thuốc!")

            self.medicine_entry.delete(0, "end")
            self.quantity_entry.delete(0, "end")
            self.unit_entry.delete(0, "end")
            self.price_entry.delete(0, "end")

            self.refresh_tree()
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng và giá phải là số nguyên")

    def subtract_medicine(self):
        """Xuất thuốc khỏi kho"""
        item_id = self.get_selected_medicine()
        if not item_id:
            return

        values = self.tree.item(item_id, "values")
        medicine_name = values[0]
        current_qty = int(values[1])

        # Tạo cửa sổ nhập số lượng
        subtract_win = tk.Toplevel(self)
        subtract_win.title("Xuất thuốc")
        subtract_win.geometry("350x200")

        tk.Label(subtract_win, text=f"Thuốc: {medicine_name}", font=("Arial", 10)).pack(pady=10)
        ttk.Label(subtract_win, text=f"Số lượng hiện tại: {current_qty}").pack(pady=5)
        ttk.Label(subtract_win, text="Số lượng xuất:").pack(pady=5)

        qty_entry = ttk.Entry(subtract_win, width=20)
        qty_entry.pack(pady=5, padx=20)

        def subtract():
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showwarning("Thông báo", "Số lượng phải lớn hơn 0")
                    return
                if qty > current_qty:
                    messagebox.showwarning("Thông báo", f"Không đủ số lượng (chỉ có {current_qty})")
                    return

                new_qty = current_qty - qty
                self.controller.db.cursor.execute(
                    "UPDATE medicines SET quantity = ? WHERE name = ?",
                    (new_qty, medicine_name)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xuất thuốc thành công!")
                subtract_win.destroy()
                self.refresh_tree()
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng phải là số nguyên")

        ttk.Button(subtract_win, text="Xuất", command=subtract).pack(pady=15)

    def edit_medicine(self):
        """Chỉnh sửa thông tin thuốc (Tên, Số lượng, Đơn vị, Giá)"""
        item_id = self.get_selected_medicine()
        if not item_id:
            return

        values = self.tree.item(item_id, "values")
        medicine_name = values[0]
        current_qty = int(values[1])
        current_unit = values[2]
        current_price = int(values[3].replace(" VNĐ", "").replace(",", ""))

        edit_win = tk.Toplevel(self)
        edit_win.title(f"Chỉnh sửa - {medicine_name}")
        edit_win.geometry("400x250")

        tk.Label(edit_win, text=f"Chỉnh sửa: {medicine_name}", font=("Arial", 12, "bold")).pack(pady=10)

        form_frame = ttk.Frame(edit_win)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Label(form_frame, text="Số lượng:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        qty_entry = ttk.Entry(form_frame, width=20)
        qty_entry.insert(0, str(current_qty))
        qty_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Đơn vị:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        unit_entry = ttk.Entry(form_frame, width=20)
        unit_entry.insert(0, current_unit)
        unit_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Giá (VNĐ):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        price_entry = ttk.Entry(form_frame, width=20)
        price_entry.insert(0, str(current_price))
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_edit():
            try:
                new_qty = int(qty_entry.get())
                new_unit = unit_entry.get().strip()
                new_price = int(price_entry.get())

                if new_qty < 0:
                    messagebox.showwarning("Thông báo", "Số lượng không được âm")
                    return
                if not new_unit:
                    messagebox.showwarning("Thông báo", "Vui lòng nhập đơn vị")
                    return
                if new_price < 0:
                    messagebox.showwarning("Thông báo", "Giá không được âm")
                    return

                self.controller.db.cursor.execute(
                    "UPDATE medicines SET quantity = ?, unit = ?, price = ? WHERE name = ?",
                    (new_qty, new_unit, new_price, medicine_name)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                edit_win.destroy()
                self.refresh_tree()
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và giá phải là số nguyên")

        ttk.Button(form_frame, text="Lưu", command=save_edit).grid(row=3, column=0, columnspan=2, pady=20)

    def delete_medicine(self):
        """Xóa loại thuốc"""
        item_id = self.get_selected_medicine()
        if not item_id:
            return

        values = self.tree.item(item_id, "values")
        medicine_name = values[0]

        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa {medicine_name}?"):
            try:
                self.controller.db.cursor.execute("DELETE FROM medicines WHERE name = ?", (medicine_name,))
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Xóa thuốc thành công!")
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")
