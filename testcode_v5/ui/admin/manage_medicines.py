import tkinter as tk
from tkinter import ttk, messagebox

class ManageMedicinesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ KHO THUỐC", font=("Arial", 16, "bold")).pack(pady=20)
        
        # === FORM NHẬP/XUẤT THUỐC ===
        form_frame = ttk.LabelFrame(self, text="Nhập/Xuất thuốc", padding=10)
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
        
        btn_frame_form = ttk.Frame(form_frame)
        btn_frame_form.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame_form, text="Nhập kho", command=self.add_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame_form, text="Xóa khỏi kho", command=self.subtract_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame_form, text="Làm mới", command=self.refresh_tree).pack(side="left", padx=5)
        
        # === SEARCH BAR ===
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_medicines())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)
        
        # === TREEVIEW ===
        self.tree = ttk.Treeview(self, columns=("medicine", "quantity", "unit","price"), show="headings", height=12)
        self.tree.heading("medicine", text="Tên thuốc")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.heading("unit", text="Đơn vị")

        self.tree.column("medicine", width=300)
        self.tree.column("quantity", width=100)
        self.tree.column("unit", width=100)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
        
        # === BUTTON FRAME ===
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        ttk.Button(btn_frame, text="Chỉnh sửa", command=self.edit_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_medicine).pack(side="left", padx=5)
        
        self.all_medicines = {}
        self.refresh_tree()

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
                self.tree.insert("", "end", values=(name, info["quantity"], info["unit"],info.get("price","")))

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
        
        if not name or not quantity or not unit:
            messagebox.showwarning("Thông báo", "Vui lòng điền đầy đủ thông tin")
            return
        
        try:
            qty = int(quantity)
            if qty <= 0:
                messagebox.showwarning("Thông báo", "Số lượng phải lớn hơn 0")
                return
            
            self.controller.db.add_medicine(name, qty, unit)
            messagebox.showinfo("Thành công", "Đã cập nhật kho thuốc!")
            
            self.medicine_entry.delete(0, "end")
            self.quantity_entry.delete(0, "end")
            self.unit_entry.delete(0, "end")
            self.price_entry.delete(0, "end")
            
            self.refresh_tree()
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên")

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
        subtract_win.geometry("300x150")
        
        ttk.Label(subtract_win, text=f"Thuốc: {medicine_name}", font=("Arial", 10)).pack(pady=10)
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
        """Chỉnh sửa thông tin thuốc"""
        item_id = self.get_selected_medicine()
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        medicine_name = values[0]
        current_qty = int(values[1])
        current_unit = values[2]
        
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Chỉnh sửa - {medicine_name}")
        edit_win.geometry("350x180")
        
        ttk.Label(edit_win, text=f"Chỉnh sửa: {medicine_name}", font=("Arial", 12, "bold")).pack(pady=10)
        
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

        
        def save_edit():
            try:
                new_qty = int(qty_entry.get())
                new_unit = unit_entry.get().strip()
                
                if new_qty < 0:
                    messagebox.showwarning("Thông báo", "Số lượng không được âm")
                    return
                if not new_unit:
                    messagebox.showwarning("Thông báo", "Vui lòng nhập đơn vị")
                    return
                
                self.controller.db.cursor.execute(
                    "UPDATE medicines SET quantity = ?, unit = ? WHERE name = ?",
                    (new_qty, new_unit, medicine_name)
                )
                self.controller.db.conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                edit_win.destroy()
                self.refresh_tree()
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng phải là số nguyên")
        
        ttk.Button(form_frame, text="Lưu", command=save_edit).grid(row=2, column=0, columnspan=2, pady=20)

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
