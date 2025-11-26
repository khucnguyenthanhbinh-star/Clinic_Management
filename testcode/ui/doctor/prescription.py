import tkinter as tk
from tkinter import ttk, messagebox

class PrescriptionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="KÊ ĐƠN THUỐC", font=("Arial", 16, "bold")).pack(pady=20)
        frame = ttk.Frame(self)
        frame.pack(pady=20)
        
        # Lấy danh sách thuốc từ DB
        self.medicines_data = self.controller.db.get_medicines()
        medicine_names = list(self.medicines_data.keys())
        
        ttk.Label(frame, text="Chọn thuốc:").grid(row=0, column=0, pady=10, sticky="e")
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(frame, textvariable=self.medicine_var, width=23, values=medicine_names)
        self.medicine_combo.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Số lượng:").grid(row=1, column=0, pady=10, sticky="e")
        self.quantity_entry = ttk.Entry(frame, width=25)
        self.quantity_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Hướng dẫn:").grid(row=2, column=0, pady=10, sticky="ne")
        self.instruction_text = tk.Text(frame, width=30, height=3)
        self.instruction_text.grid(row=2, column=1, pady=10)
        
        # Treeview hiển thị đơn thuốc đang kê
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=("medicine", "quantity", "instruction"), show="headings")
        self.tree.heading("medicine", text="Thuốc")
        self.tree.heading("quantity", text="Số lượng")
        self.tree.heading("instruction", text="Hướng dẫn")
        self.tree.pack(fill="both", expand=True)
        
        ttk.Button(frame, text="Thêm thuốc", command=self.add_medicine).grid(row=3, column=0, columnspan=2, pady=10)

    def add_medicine(self):
        medicine = self.medicine_var.get()
        quantity = self.quantity_entry.get()
        instruction = self.instruction_text.get("1.0", "end-1c")
        
        if medicine and quantity:
            # Kiểm tra tồn kho (Logic cơ bản)
            if int(quantity) > self.medicines_data[medicine]["quantity"]:
                messagebox.showwarning("Cảnh báo", f"Trong kho chỉ còn {self.medicines_data[medicine]['quantity']} {self.medicines_data[medicine]['unit']}")
                return

            self.tree.insert("", "end", values=(medicine, quantity, instruction))
            
            # Clear form
            self.medicine_combo.set("")
            self.quantity_entry.delete(0, "end")
            self.instruction_text.delete("1.0", "end")