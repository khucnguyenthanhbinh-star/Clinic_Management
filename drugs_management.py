# ===================== FILE: clinic_management_system_csv.py =====================
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os

# Tên file CSV
DRUGS_FILE = "drugs_inventory.csv"
LOG_FILE = "inventory_log.csv"

# ===================== ĐỌC/GHI FILE CSV =====================
def load_drugs_from_csv():
    drugs = []
    if os.path.exists(DRUGS_FILE):
        with open(DRUGS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["id"] = int(row["id"])
                row["import_qty"] = int(row["import_qty"])
                row["sold_qty"] = int(row["sold_qty"])
                row["stock"] = int(row["stock"])
                row["import_price"] = int(row["import_price"])
                row["sell_price"] = int(row["sell_price"])
                drugs.append(row)
    else:
        # Dữ liệu mẫu lần đầu chạy
        drugs = [
            {"id": 1, "name": "Paracetamol 500mg", "unit": "Viên", "import_qty": 500, "sold_qty": 280, "stock": 220, "import_price": 1500, "sell_price": 3000, "expiry": "2026-12-31"},
            {"id": 2, "name": "Amoxicillin 500mg", "unit": "Viên", "import_qty": 300, "sold_qty": 150, "stock": 150, "import_price": 8000, "sell_price": 15000, "expiry": "2026-08-15"},
            {"id": 3, "name": "Vitamin C 1000mg", "unit": "Viên", "import_qty": 800, "sold_qty": 620, "stock": 180, "import_price": 2000, "sell_price": 5000, "expiry": "2027-03-20"},
            {"id": 4, "name": "Thuốc ho Prospan", "unit": "Chai", "import_qty": 200, "sold_qty": 90, "stock": 110, "import_price": 85000, "sell_price": 120000, "expiry": "2026-11-10"},
            {"id": 5, "name": "Panadol Extra", "unit": "Vỉ", "import_qty": 400, "sold_qty": 310, "stock": 90, "import_price": 25000, "sell_price": 38000, "expiry": "2026-09-30"},
            {"id": 6, "name": "Berberin 100mg", "unit": "Viên", "import_qty": 600, "sold_qty": 350, "stock": 250, "import_price": 5000, "sell_price": 10000, "expiry": "2027-01-15"},
        ]
        save_drugs_to_csv(drugs)
    return drugs

def save_drugs_to_csv(drugs_list):
    with open(DRUGS_FILE, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["id", "name", "unit", "import_qty", "sold_qty", "stock", "import_price", "sell_price", "expiry"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(drugs_list)

def load_log_from_csv():
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["quantity"] = int(row["quantity"])
                row["price"] = int(row["price"])
                log.append(row)
    return log

def save_log_to_csv(log_list):
    with open(LOG_FILE, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["time", "action", "drug_name", "quantity", "price"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_list)

# ===================== KHỞI TẠO DỮ LIỆU =====================
drugs = load_drugs_from_csv()
inventory_log = load_log_from_csv()
next_drug_id = max((d["id"] for d in drugs), default=0) + 1

# ===================== GIAO DIỆN =====================
root = tk.Tk()
root.title("QUẢN LÝ KHO THUỐC - LƯU TRỮ BẰNG CSV")
root.geometry("1250x750")
root.configure(bg="#f5f7fa")

tk.Label(root, text="QUẢN LÝ KHO THUỐC PHÒNG KHÁM", font=("Helvetica", 20, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(pady=15)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=10)

# ===================== TAB 1: DANH SÁCH THUỐC =====================
tab_list = tk.Frame(notebook, bg="#f5f7fa")
notebook.add(tab_list, text="Danh Sách Thuốc")

tree_drug = ttk.Treeview(tab_list, columns=("ID","Tên","ĐV","Tồn","Nhập","Bán","HSD","TT"), show="headings")
for col, text in zip(tree_drug["columns"], ["ID","Tên thuốc","ĐV","Tồn kho","Giá nhập","Giá bán","Hạn dùng","Trạng thái"]):
    tree_drug.heading(col, text=text)
    tree_drug.column(col, anchor="center", width=110)
tree_drug.column("Tên", width=250, anchor="w")
tree_drug.pack(padx=20, pady=10, fill="both", expand=True)

def load_drugs():
    for i in tree_drug.get_children(): tree_drug.delete(i)
    for d in drugs:
        status = "Cảnh báo" if d["stock"] < 100 else "Bình thường" if d["stock"] < 200 else "Tốt"
        tree_drug.insert("", "end", values=(
            d["id"], d["name"], d["unit"], d["stock"],
            f"{d['import_price']:,}", f"{d['sell_price']:,}", d["expiry"], status
        ), tags=(status,))
    tree_drug.tag_configure("Cảnh báo", background="#ffebee")
    tree_drug.tag_configure("Bình thường", background="#fff3e0")
    tree_drug.tag_configure("Tốt", background="#e8f5e9")

# ===================== TAB 2: NHẬP KHO =====================
tab_import = tk.Frame(notebook, bg="#f5f7fa")
notebook.add(tab_import, text="Nhập Kho")

form = tk.LabelFrame(tab_import, text="Nhập kho thuốc", font=("Arial", 12, "bold"), bg="#f5f7fa")
form.pack(pady=20, padx=30, fill="x")

entries = {}
labels = ["Tên thuốc", "Đơn vị", "Số lượng nhập", "Giá nhập (VNĐ)", "Giá bán (VNĐ)", "Hạn sử dụng (YYYY-MM-DD)"]
defaults = ["", "Viên", "100", "2000", "5000", datetime.now().strftime("%Y-%m-%d")]

for i, (label, default) in enumerate(zip(labels, defaults)):
    tk.Label(form, text=label + ":", bg="#f5f7fa").grid(row=i, column=0, sticky="w", padx=10, pady=8)
    entry = tk.Entry(form, width=35, font=("Arial", 10))
    entry.insert(0, default)
    entry.grid(row=i, column=1, padx=10, pady=8)
    entries[label] = entry

def add_drug():
    global next_drug_id
    try:
        name = entries["Tên thuốc"].get().strip()
        if not name: raise ValueError("Tên thuốc không được để trống!")

        qty = int(entries["Số lượng nhập"].get())
        import_p = int(entries["Giá nhập (VNĐ)"].get())
        sell_p = int(entries["Giá bán (VNĐ)"].get())
        expiry = entries["Hạn sử dụng (YYYY-MM-DD)"].get()
        datetime.strptime(expiry, "%Y-%m-%d")

        # Tìm thuốc đã có
        existing = next((d for d in drugs if d["name"].lower() == name.lower()), None)
        if existing:
            existing["import_qty"] += qty
            existing["stock"] += qty
            existing["import_price"] = import_p
            existing["sell_price"] = sell_p
            existing["expiry"] = expiry
            msg = f"Cập nhật kho: +{qty} {name}"
        else:
            drugs.append({
                "id": next_drug_id, "name": name, "unit": entries["Đơn vị"].get(),
                "import_qty": qty, "sold_qty": 0, "stock": qty,
                "import_price": import_p, "sell_price": sell_p, "expiry": expiry
            })
            msg = f"Thêm mới thuốc: {name}"
            next_drug_id += 1

        # Ghi log + lưu file
        inventory_log.append({
            "time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "action": "Nhập kho",
            "drug_name": name,
            "quantity": qty,
            "price": import_p
        })
        save_drugs_to_csv(drugs)
        save_log_to_csv(inventory_log)

        messagebox.showinfo("Thành công", msg)
        load_drugs()
        load_log()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

tk.Button(form, text="NHẬP KHO", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), command=add_drug, width=20, height=2).grid(row=6, column=0, columnspan=2, pady=20)

# ===================== TAB 3: XUẤT KHO =====================
tab_export = tk.Frame(notebook, bg="#f5f7fa")
notebook.add(tab_export, text="Xuất Kho")

export_form = tk.LabelFrame(tab_export, text="Xuất thuốc", font=("Arial", 12, "bold"), bg="#f5f7fa")
export_form.pack(pady=20, padx=30, fill="x")

tk.Label(export_form, text="Chọn thuốc:", bg="#f5f7fa").grid(row=0, column=0, sticky="w", padx=10, pady=10)
drug_combo = ttk.Combobox(export_form, values=[d["name"] for d in drugs], width=40, state="readonly")
drug_combo.grid(row=0, column=1, padx=10, pady=10)

tk.Label(export_form, text="Số lượng xuất:", bg="#f5f7fa").grid(row=1, column=0, sticky="w", padx=10, pady=10)
qty_export = tk.Entry(export_form, width=20)
qty_export.insert(0, "1")
qty_export.grid(row=1, column=1, sticky="w", padx=10, pady=10)

def export_drug():
    try:
        name = drug_combo.get()
        if not name: raise ValueError("Chưa chọn thuốc!")
        qty = int(qty_export.get())
        drug = next(d for d in drugs if d["name"] == name)
        if drug["stock"] < qty: raise ValueError(f"Chỉ còn {drug['stock']} {drug['unit']}!")

        drug["sold_qty"] += qty
        drug["stock"] -= qty

        inventory_log.append({
            "time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "action": "Xuất kho",
            "drug_name": name,
            "quantity": qty,
            "price": drug["sell_price"]
        })

        save_drugs_to_csv(drugs)
        save_log_to_csv(inventory_log)
        messagebox.showinfo("Thành công", f"Đã xuất {qty} {drug['unit']} {name}")
        load_drugs()
        load_log()
        drug_combo["values"] = [d["name"] for d in drugs]  # Cập nhật combobox
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

tk.Button(export_form, text="XUẤT KHO", bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), command=export_drug, width=20, height=2).grid(row=2, column=0, columnspan=2, pady=20)

# ===================== TAB 4: LỊCH SỬ =====================
tab_log = tk.Frame(notebook, bg="#f5f7fa")
notebook.add(tab_log, text="Lịch Sử Kho")

tree_log = ttk.Treeview(tab_log, columns=("Time","Action","Drug","Qty","Price"), show="headings", height=20)
for col, text in zip(tree_log["columns"], ["Thời gian","Hành động","Tên thuốc","Số lượng","Giá"]):
    tree_log.heading(col, text=text)
    tree_log.column(col, width=150, anchor="center")
tree_log.column("Drug", width=280, anchor="w")
tree_log.pack(padx=20, pady=10, fill="both", expand=True)

def load_log():
    for i in tree_log.get_children(): tree_log.delete(i)
    for log in sorted(inventory_log, key=lambda x: x["time"], reverse=True):
        tree_log.insert("", "end", values=(
            log["time"], log["action"], log["drug_name"], log["quantity"], f"{log['price']:,} VNĐ"
        ))

# ===================== KHỞI ĐỘNG =====================
load_drugs()
load_log()

root.mainloop()