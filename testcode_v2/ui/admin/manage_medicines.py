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
        
        ttk.Button(form_frame, text="Nhập kho", command=self.add_medicine).grid(row=3, column=0, columnspan=2, pady=10)
        
        self.tree = ttk.Treeview(self, columns=("medicine", "quantity", "unit"), show="headings")
        self.tree.heading("medicine", text="Tên thuốc")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.heading("unit", text="Đơn vị")
        self.tree.pack(fill="both", expand=True, padx=20)
        
        self.refresh_tree()

    def add_medicine(self):
        name = self.medicine_entry.get()
        quantity = self.quantity_entry.get()
        unit = self.unit_entry.get()
        
        if name and quantity and unit:
            self.controller.db.add_medicine(name, quantity, unit)
            self.refresh_tree()
            messagebox.showinfo("Thành công", "Đã cập nhật kho thuốc!")
            
            # Clear input
            self.medicine_entry.delete(0, "end")
            self.quantity_entry.delete(0, "end")

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        medicines = self.controller.db.get_medicines()
        for med_name, info in medicines.items():
            self.tree.insert("", "end", values=(med_name, info["quantity"], info["unit"]))