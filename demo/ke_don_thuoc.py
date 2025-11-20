# ke_don_thuoc.py - PHIÊN BẢN HOÀN CHỈNH, KHÔNG LỖI (20/11/2025)
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
import json


class ClinicPrescriptionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Kê Đơn Thuốc - Phòng khám")
        self.root.geometry("1350x780")
        self.root.configure(bg="#f8f9fa")

        # Đường dẫn file CSV
        self.DRUGS_FILE = "drugs_inventory.csv"
        self.LOG_FILE = "inventory_log.csv"
        self.PRESCRIPTION_LOG_FILE = "prescription_log.csv"

        # Load dữ liệu
        self.drugs = self.load_drugs()
        self.logs = self.load_logs()
        self.prescription_logs = self.load_prescription_logs()

        self.current_doctor = "BS. Nguyễn Văn A"

        self.create_ui()

    # ==================== ĐỌC THUỐC - TỰ ĐỘNG XỬ LÝ ENCODING ====================
    def load_drugs(self):
        drugs = []
        if not os.path.exists(self.DRUGS_FILE):
            return drugs

        encodings = ['utf-8', 'utf-8-sig', 'cp1258']  # Thử lần lượt
        for enc in encodings:
            try:
                with open(self.DRUGS_FILE, mode='r', encoding=enc) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row["id"] = int(row.get("id", 0))
                        row["import_qty"] = int(row.get("import_qty", 0))
                        row["sold_qty"] = int(row.get("sold_qty", 0))
                        row["stock"] = int(row.get("stock", 0))
                        row["import_price"] = int(row.get("import_price", 0))
                        row["sell_price"] = int(row.get("sell_price", 0))
                        drugs.append(row)
                print(f"Đọc drugs_inventory.csv thành công với encoding: {enc}")
                return drugs
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Lỗi khi đọc drugs với {enc}: {e}")
                continue

        messagebox.showerror("Lỗi", "Không đọc được file drugs_inventory.csv\n"
                                    "Hãy mở bằng Notepad → Save As → Encoding: UTF-8")
        return drugs

    def save_drugs(self):
        with open(self.DRUGS_FILE, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["id", "name", "unit", "import_qty", "sold_qty", "stock",
                          "import_price", "sell_price", "expiry"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.drugs)

    # ==================== LOG KHO ====================
    def load_logs(self):
        logs = []
        if not os.path.exists(self.LOG_FILE):
            return logs
        try:
            with open(self.LOG_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["quantity"] = int(row.get("quantity", 0))
                    row["price"] = int(row.get("price", 0))
                    logs.append(row)
        except:
            pass
        return logs

    def save_log(self, action, drug_name, qty, price):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_log = {"time": timestamp, "action": action, "drug_name": drug_name,
                   "quantity": qty, "price": price}
        self.logs.insert(0, new_log)
        with open(self.LOG_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["time", "action", "drug_name", "quantity", "price"])
            writer.writeheader()
            writer.writerows(self.logs)

    # ==================== LỊCH SỬ KÊ ĐƠN - SỬA LỖI JSON ====================
    def load_prescription_logs(self):
        logs = []
        if not os.path.exists(self.PRESCRIPTION_LOG_FILE):
            with open(self.PRESCRIPTION_LOG_FILE, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["time", "doctor", "details"])
                writer.writeheader()
            return logs

        with open(self.PRESCRIPTION_LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    details_str = row["details"]
                    if isinstance(details_str, str):
                        row["details"] = json.loads(details_str)
                    else:
                        row["details"] = []
                except:
                    row["details"] = []
                logs.append(row)
        return logs

    def save_prescription_log(self, details):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_log = {
            "time": timestamp,
            "doctor": self.current_doctor,
            "details": json.dumps(details, ensure_ascii=False)
        }
        self.prescription_logs.insert(0, new_log)
        with open(self.PRESCRIPTION_LOG_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["time", "doctor", "details"])
            writer.writeheader()
            for log in self.prescription_logs:
                log_copy = log.copy()
                if isinstance(log_copy["details"], list):
                    log_copy["details"] = json.dumps(log_copy["details"], ensure_ascii=False)
                writer.writerow(log_copy)

    # ==================== GIAO DIỆN ====================
    def create_ui(self):
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="HỆ THỐNG KÊ ĐƠN THUỐC", font=("Helvetica", 18, "bold"),
                 fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"Bác sĩ: {self.current_doctor}", font=("Arial", 12),
                 fg="#ecf0f1", bg="#2c3e50").pack(side="right", padx=20, pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_prescription_tab()
        self.create_history_tab()

    def create_prescription_tab(self):
        tab = tk.Frame(self.notebook, bg="#f8f9fa")
        self.notebook.add(tab, text="Kê Đơn Thuốc")

        left_frame = tk.LabelFrame(tab, text=" Kê đơn thuốc ", font=("Arial", 14, "bold"), bg="#f8f9fa")
        left_frame.pack(side="left", fill="both", padx=(0, 10), pady=10)

        # Chọn thuốc
        tk.Label(left_frame, text="Tên thuốc:", bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(left_frame, textvariable=self.medicine_var, width=40, state="readonly")
        self.medicine_combo['values'] = [d["name"] for d in self.drugs if int(d["stock"]) > 0]
        self.medicine_combo.grid(row=0, column=1, padx=10, pady=10)
        self.medicine_combo.bind("<<ComboboxSelected>>", self.update_stock_info)

        self.stock_label = tk.Label(left_frame, text="Tồn kho: --", bg="#f8f9fa", fg="#e67e22", font=("Arial", 11, "bold"))
        self.stock_label.grid(row=1, column=1, sticky="w", padx=10)

        tk.Label(left_frame, text="Số lượng:", bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.qty_entry = tk.Entry(left_frame, width=20)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        tk.Label(left_frame, text="Hướng dẫn:", bg="#f8f9fa").grid(row=3, column=0, sticky="nw", pady=10, padx=10)
        self.instruction_text = tk.Text(left_frame, width=40, height=4)
        self.instruction_text.grid(row=3, column=1, padx=10, pady=10)

        tk.Button(left_frame, text="THÊM VÀO ĐƠN", bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                  command=self.add_to_prescription, height=2).grid(row=4, column=0, columnspan=2, pady=20)

        # Danh sách thuốc hiện tại
        right_frame = tk.LabelFrame(tab, text=" Đơn thuốc hiện tại ", font=("Arial", 14, "bold"))
        right_frame.pack(side="right", fill="both", expand=True, pady=10)

        columns = ("name", "qty", "unit", "instruction")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.tree.heading("name", text="Tên thuốc")
        self.tree.heading("qty", text="SL")
        self.tree.heading("unit", text="ĐV")
        self.tree.heading("instruction", text="Hướng dẫn sử dụng")
        self.tree.column("name", width=260)
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("unit", width=80, anchor="center")
        self.tree.column("instruction", width=320)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Xóa mục", bg="#e74c3c", fg="white", command=self.remove_item).pack(side="left", padx=5)
        tk.Button(btn_frame, text="LƯU ĐƠN THUỐC", bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                  command=self.save_prescription, height=2, width=20).pack(side="right", padx=10)

    def create_history_tab(self):
        tab = tk.Frame(self.notebook, bg="#f8f9fa")
        self.notebook.add(tab, text="Lịch Sử Kê Đơn")

        columns = ("time", "doctor", "details")
        self.history_tree = ttk.Treeview(tab, columns=columns, show="headings", height=22)
        self.history_tree.heading("time", text="Thời gian")
        self.history_tree.heading("doctor", text="Bác sĩ")
        self.history_tree.heading("details", text="Chi tiết đơn thuốc")
        self.history_tree.column("time", width=150, anchor="center")
        self.history_tree.column("doctor", width=180)
        self.history_tree.column("details", width=800)
        self.history_tree.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_history()

    def load_history(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        for log in self.prescription_logs:
            details_list = log.get("details", [])
            if isinstance(details_list, str):
                try:
                    details_list = json.loads(details_list)
                except:
                    details_list = []
            details_str = ";  ".join([
                f"{item.get('name','')} - {item.get('qty','')} {item.get('unit','')} ({item.get('instruction','')})"
                for item in details_list
            ]) if details_list else "Không có thuốc"
            self.history_tree.insert("", "end", values=(log.get("time", ""), log.get("doctor", ""), details_str))

    def update_stock_info(self, event=None):
        name = self.medicine_var.get()
        drug = next((d for d in self.drugs if d["name"] == name), None)
        if drug:
            color = "red" if int(drug["stock"]) < 50 else "#e67e22" if int(drug["stock"]) < 100 else "green"
            self.stock_label.config(text=f"Tồn kho: {drug['stock']} {drug['unit']}  |  Giá: {int(drug['sell_price']):,} VNĐ",
                                    fg=color)

    def add_to_prescription(self):
        name = self.medicine_var.get()
        qty_str = self.qty_entry.get()
        instruction = self.instruction_text.get("1.0", "end-1c").strip()

        if not name:
            messagebox.showwarning("Lỗi", "Vui lòng chọn thuốc!")
            return
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showwarning("Lỗi", "Số lượng phải là số dương!")
            return

        qty = int(qty_str)
        drug = next(d for d in self.drugs if d["name"] == name)
        if int(drug["stock"]) < qty:
            messagebox.showerror("Hết hàng", f"Chỉ còn {drug['stock']} {drug['unit']} {name}!")
            return

        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == name:
                messagebox.showwarning("Trùng", "Thuốc đã có trong đơn!")
                return

        self.tree.insert("", "end", values=(name, qty, drug["unit"], instruction or "Uống theo chỉ định"))
        self.medicine_combo.set("")
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, "1")
        self.instruction_text.delete("1.0", "end")
        self.stock_label.config(text="Tồn kho: --")

    def remove_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn", "Vui lòng chọn thuốc cần xóa!")
            return
        self.tree.delete(selected)

    def save_prescription(self):
        if not self.tree.get_children():
            messagebox.showwarning("Rỗng", "Chưa có thuốc nào trong đơn!")
            return

        if not messagebox.askyesno("Xác nhận", "Lưu đơn và xuất thuốc khỏi kho?"):
            return

        prescription_details = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            name, qty_str, unit, instruction = values[0], values[1], values[2], values[3]
            qty = int(qty_str)

            drug = next(d for d in self.drugs if d["name"] == name)
            drug["sold_qty"] = int(drug["sold_qty"]) + qty
            drug["stock"] = int(drug["stock"]) - qty

            self.save_log("Xuất kho", name, qty, int(drug["sell_price"]))

            prescription_details.append({
                "name": name, "qty": qty, "unit": unit, "instruction": instruction
            })

        self.save_drugs()
        self.save_prescription_log(prescription_details)

        messagebox.showinfo("Thành công", f"Đã lưu đơn và xuất kho!\nTổng: {len(self.tree.get_children())} loại thuốc")

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.medicine_combo['values'] = [d["name"] for d in self.drugs if int(d["stock"]) > 0]
        self.load_history()


# ===================== CHẠY CHƯƠNG TRÌNH =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicPrescriptionSystem(root)
    root.mainloop()