import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import random

# ====================== DỮ LIỆU MẪU (CHO BÁO CÁO) ======================
appointments = []
revenues = []
drugs = []
doctors = ["BS. Nguyễn Văn A", "BS. Trần Thị B", "BS. Lê Văn C"]

def init_data():
    # Dữ liệu lịch hẹn + doanh thu khám
    patients = ["Nguyễn Văn Nam", "Trần Thị Lan", "Lê Minh Tuấn", "Phạm Ngọc Anh", "Hoàng Thị Mai", "Đỗ Văn Hùng"]
    statuses = ["Đã khám xong", "Đã xác nhận", "Đang chờ xác nhận", "Đã hủy"]
    
    for i in range(60):
        doctor = random.choice(doctors)
        patient = random.choice(patients)
        days_ago = random.randint(0, 30)
        hour = random.choice([8,9,10,11,14,15,16,17])
        minute = random.choice([0, 30])
        time = datetime.now() - timedelta(days=days_ago)
        time = time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        status = random.choice(statuses)
        fee = 0
        if status == "Đã khám xong":
            fee = random.choice([200000, 250000, 300000, 350000])
            revenues.append({"date": time.date(), "type": "Khám bệnh", "amount": fee, "doctor": doctor})
        
        appointments.append({
            "patient": patient,
            "doctor": doctor,
            "time": time,
            "status": status,
            "fee": fee
        })
    
    # Dữ liệu thuốc
    drug_names = ["Paracetamol 500mg", "Amoxicillin 500mg", "Vitamin C 1000mg", "Thuốc ho Prospan", "Panadol Extra", "Berberin"]
    for name in drug_names:
        import_qty = random.randint(100, 600)
        sold_qty = random.randint(20, import_qty - 20)
        drugs.append({
            "name": name,
            "import_qty": import_qty,
            "sold_qty": sold_qty,
            "stock": import_qty - sold_qty,
            "import_price": random.randint(800, 5000),
            "sell_price": random.randint(10000, 35000)
        })
        # Doanh thu bán thuốc
        if sold_qty > 0:
            revenue = sold_qty * random.randint(12000, 30000)
            revenues.append({
                "date": (datetime.now() - timedelta(days=random.randint(0,20))).date(),
                "type": "Bán thuốc",
                "amount": revenue,
                "doctor": "Kho thuốc"
            })

init_data()  # Tạo dữ liệu mẫu

# ====================== GIAO DIỆN ADMIN DASHBOARD ======================
root = tk.Tk()
root.title("ADMIN - BÁO CÁO PHÒNG KHÁM")
root.geometry("1100x700")
root.configure(bg="#f4f6f9")

# Tiêu đề
title = tk.Label(root, text="BẢNG ĐIỀU KHIỂN ADMIN", font=("Helvetica", 20, "bold"), bg="#f4f6f9", fg="#2c3e50")
title.pack(pady=15)

# Notebook (tab)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

# ====================== TAB 1: TỔNG DOANH THU ======================
tab1 = tk.Frame(notebook, bg="#f4f6f9")
notebook.add(tab1, text="Tổng Doanh Thu")

total_revenue = sum(r["amount"] for r in revenues)
tk.Label(tab1, text=f"TỔNG DOANH THU: {total_revenue:,} VNĐ", 
         font=("Arial", 18, "bold"), fg="#27ae60", bg="#f4f6f9").pack(pady=20)

# Phân loại doanh thu
revenue_by_type = {"Khám bệnh": 0, "Bán thuốc": 0}
for r in revenues:
    revenue_by_type[r["type"]] += r["amount"]

tk.Label(tab1, text=f"• Doanh thu từ khám bệnh: {revenue_by_type['Khám bệnh']:,} VNĐ", 
         font=("Arial", 14), bg="#f4f6f9").pack(anchor="w", padx=100)
tk.Label(tab1, text=f"• Doanh thu từ bán thuốc: {revenue_by_type['Bán thuốc']:,} VNĐ", 
         font=("Arial", 14), bg="#f4f6f9").pack(anchor="w", padx=100)

# ====================== TAB 2: THỐNG KÊ THUỐC ======================
tab2 = tk.Frame(notebook, bg="#f4f6f9")
notebook.add(tab2, text="Quản Lý Thuốc")

tree_drug = ttk.Treeview(tab2, columns=("Tên", "Nhập", "Bán", "Tồn", "Giá bán"), show="headings", height=15)
tree_drug.heading("Tên", text="Tên thuốc")
tree_drug.heading("Nhập", text="Số lượng nhập")
tree_drug.heading("Bán", text="Đã bán")
tree_drug.heading("Tồn", text="Tồn kho")
tree_drug.heading("Giá bán", text="Giá bán (VNĐ)")

tree_drug.column("Tên", width=200)
tree_drug.column("Nhập", width=100, anchor="center")
tree_drug.column("Bán", width=100, anchor="center")
tree_drug.column("Tồn", width=100, anchor="center")
tree_drug.column("Giá bán", width=120, anchor="e")

for drug in drugs:
    tree_drug.insert("", "end", values=(
        drug["name"],
        drug["import_qty"],
        drug["sold_qty"],
        drug["stock"],
        f"{drug['sell_price']:,}"
    ))
tree_drug.pack(padx=20, pady=20, fill="both", expand=True)

# Tổng tồn kho
total_stock = sum(d["stock"] for d in drugs)
tk.Label(tab2, text=f"TỔNG TỒN KHO: {total_stock} hộp/viên", font=("Arial", 12, "bold"), bg="#f4f6f9").pack(pady=5)

# ====================== TAB 3: TẤT CẢ LỊCH HẸN ======================
tab3 = tk.Frame(notebook, bg="#f4f6f9")
notebook.add(tab3, text="Danh Sách Lịch Hẹn")

filter_frame = tk.Frame(tab3, bg="#f4f6f9")
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Lọc theo trạng thái:", bg="#f4f6f9").pack(side="left", padx=5)
status_filter = ttk.Combobox(filter_frame, values=["Tất cả", "Đã khám xong", "Đã xác nhận", "Đang chờ xác nhận", "Đã hủy"], width=20)
status_filter.set("Tất cả")
status_filter.pack(side="left", padx=5)

tree_app = ttk.Treeview(tab3, columns=("Thời gian", "Bệnh nhân", "Bác sĩ", "Trạng thái", "Phí khám"), show="headings", height=18)
tree_app.heading("Thời gian", text="Thời gian")
tree_app.heading("Bệnh nhân", text="Bệnh nhân")
tree_app.heading("Bác sĩ", text="Bác sĩ")
tree_app.heading("Trạng thái", text="Trạng thái")
tree_app.heading("Phí khám", text="Phí khám (VNĐ)")

for col in tree_app["columns"]:
    tree_app.column(col, width=140, anchor="center")
tree_app.column("Bệnh nhân", width=180)
tree_app.column("Thời gian", width=160)

def load_appointments():
    for item in tree_app.get_children():
        tree_app.delete(item)
    status = status_filter.get()
    for app in sorted(appointments, key=lambda x: x["time"], reverse=True):
        if status == "Tất cả" or app["status"] == status:
            tree_app.insert("", "end", values=(
                app["time"].strftime("%d/%m/%Y %H:%M"),
                app["patient"],
                app["doctor"],
                app["status"],
                f"{app['fee']:,}" if app['fee'] > 0 else "-"
            ))

status_filter.bind("<<ComboboxSelected>>", lambda e: load_appointments())
tree_app.pack(padx=20, pady=10, fill="both", expand=True)
load_appointments()

# ====================== TAB 4: TIẾN ĐỘ BÁC SĨ ======================
tab4 = tk.Frame(notebook, bg="#f4f6f9")
notebook.add(tab4, text="Tiến Độ Bác Sĩ")

doctor_stats = {}
for app in appointments:
    if app["status"] == "Đã khám xong":
        doc = app["doctor"]
        date = app["time"].date()
        if doc not in doctor_stats:
            doctor_stats[doc] = {}
        doctor_stats[doc][date] = doctor_stats[doc].get(date, 0) + 1

tk.Label(tab4, text="SỐ BỆNH NHÂN ĐÃ KHÁM THEO NGÀY", font=("Arial", 14, "bold"), bg="#f4f6f9").pack(pady=10)

tree_doc = ttk.Treeview(tab4, columns=("Bác sĩ", "Ngày", "Số bệnh nhân"), show="headings", height=18)
tree_doc.heading("Bác sĩ", text="Bác sĩ")
tree_doc.heading("Ngày", text="Ngày khám")
tree_doc.heading("Số bệnh nhân", text="Số bệnh nhân")

tree_doc.column("Bác sĩ", width=200)
tree_doc.column("Ngày", width=150, anchor="center")
tree_doc.column("Số bệnh nhân", width=150, anchor="center")

for doc, dates in doctor_stats.items():
    for date, count in dates.items():
        tree_doc.insert("", "end", values=(doc, date.strftime("%d/%m/%Y"), count))

tree_doc.pack(padx=20, pady=10, fill="both", expand=True)

# ====================== CHẠY CHƯƠNG TRÌNH ======================
root.mainloop()