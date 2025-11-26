import tkinter as tk
from tkinter import ttk, messagebox

class ManageMedicinesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ KHO THUỐC", font=("Arial", 16, "bold")).pack(pady=20)
        
        form_frame = ttk.LabelFrame(self, text="Nhập/Xuất thuốc", padding=10)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(form_frame, text="Tên thuốc:").grid(row=0, column=0, pady=5, sticky="e")
        self.medicine_entry = ttk.Entry(form_frame, width=25)
        self.medicine_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Số lượng:").grid(row=1, column=0, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(form_frame, width=25)
        self.quantity_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text="Đơn vị:").grid(row=2, column=0, pady=5, sticky="e")
        self.unit_entry = ttk.Entry(form_frame, width=25)
        self.unit_entry.grid(row=2, column=1, pady=5)
        
        btn_form_frame = ttk.Frame(form_frame)
        btn_form_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_form_frame, text="Nhập kho", command=self.add_medicine).pack(side="left", padx=5)
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=5)
        ttk.Button(btn_frame, text="Sửa số lượng", command=self.edit_quantity).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete_medicine).pack(side="left", padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, columns=("medicine", "quantity", "unit"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("medicine", text="Tên thuốc")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.heading("unit", text="Đơn vị")
        
        self.tree.column("medicine", width=200)
        self.tree.column("quantity", width=100)
        self.tree.column("unit", width=100)
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_tree()

    def add_medicine(self):
        name = self.medicine_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        unit = self.unit_entry.get().strip()
        
        if not name or not quantity or not unit:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
            return
        
        try:
            qty = int(quantity)
        except:
            messagebox.showerror("Lỗi", "Số lượng phải là số")
            return
        
        self.controller.db.add_medicine(name, qty, unit)
        self.refresh_tree()
        messagebox.showinfo("Thành công", "Đã cập nhật kho thuốc!")
        
        # Clear input
        self.medicine_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")
        self.unit_entry.delete(0, "end")

    def edit_quantity(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thuốc")
            return
        
        item = self.tree.item(selected[0])
        medicine_name = item["values"][0]
        current_qty = item["values"][1]
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Sửa số lượng: {medicine_name}")
        dialog.geometry("400x150")
        
        ttk.Label(dialog, text="Số lượng mới:").pack(padx=10, pady=10)
        qty_entry = ttk.Entry(dialog, width=25)
        qty_entry.insert(0, str(current_qty))
        qty_entry.pack(padx=10, pady=5)
        
        def update():
            try:
                new_qty = int(qty_entry.get().strip())
            except:
                messagebox.showerror("Lỗi", "Số lượng phải là số")
                return
            
            success, msg = self.controller.db.update_medicine_quantity(medicine_name, new_qty)
            if success:
                messagebox.showinfo("Thành công", "Cập nhật số lượng thành công")
                self.refresh_tree()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg)
        
        ttk.Button(dialog, text="Cập nhật", command=update).pack(pady=10)

    def delete_medicine(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thuốc")
            return
        
        item = self.tree.item(selected[0])
        medicine_name = item["values"][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {medicine_name}?"):
            success, msg = self.controller.db.delete_medicine(medicine_name)
            if success:
                messagebox.showinfo("Thành công", "Xóa thuốc thành công")
                self.refresh_tree()
            else:
                messagebox.showerror("Lỗi", msg)

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        medicines = self.controller.db.get_medicines()
        for med_name, info in medicines.items():
            self.tree.insert("", "end", values=(med_name, info["quantity"], info["unit"]))
