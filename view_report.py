# view_report.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import random


class ClinicReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADMIN - BÁO CÁO PHÒNG KHÁM")
        self.root.geometry("1150x750")
        self.root.configure(bg="#f4f6f9")

        # Dữ liệu mẫu
        self.appointments = []
        self.revenues = []
        self.drugs = []
        self.doctors = ["BS. Nguyễn Văn A", "BS. Trần Thị B", "BS. Lê Văn C"]

        self.init_sample_data()
        self.setup_ui()

    def init_sample_data(self):
        random.seed(42)  # Để kết quả giống nhau mỗi lần chạy (dễ kiểm tra)
        patients = ["Nguyễn Văn Nam", "Trần Thị Lan", "Lê Minh Tuấn",
                    "Phạm Ngọc Anh", "Hoàng Thị Mai", "Đỗ Văn Hùng"]
        statuses = ["Đã khám xong", "Đã xác nhận", "Đang chờ xác nhận", "Đã hủy"]
        drug_names = ["Paracetamol 500mg", "Amoxicillin 500mg", "Vitamin C 1000mg",
                      "Thuốc ho Prospan", "Panadol Extra", "Berberin"]

        # Tạo lịch hẹn + doanh thu khám
        for _ in range(60):
            doctor = random.choice(self.doctors)
            patient = random.choice(patients)
            days_ago = random.randint(0, 30)
            hour = random.choice([8, 9, 10, 11, 14, 15, 16, 17])
            minute = random.choice([0, 30])
            time = datetime.now() - timedelta(days=days_ago)
            time = time.replace(hour=hour, minute=minute, second=0, microsecond=0)

            status = random.choice(statuses)
            fee = 0
            if status == "Đã khám xong":
                fee = random.choice([200000, 250000, 300000, 350000])
                self.revenues.append({
                    "date": time.date(),
                    "type": "Khám bệnh",
                    "amount": fee,
                    "doctor": doctor
                })

            self.appointments.append({
                "patient": patient,
                "doctor": doctor,
                "time": time,
                "status": status,
                "fee": fee
            })

        # Tạo dữ liệu thuốc + doanh thu bán thuốc
        for name in drug_names:
            import_qty = random.randint(100, 600)
            sold_qty = random.randint(20, import_qty - 20)
            import_price = random.randint(800, 5000)
            sell_price = random.randint(10000, 35000)

            self.drugs.append({
                "name": name,
                "import_qty": import_qty,
                "sold_qty": sold_qty,
                "stock": import_qty - sold_qty,
                "import_price": import_price,
                "sell_price": sell_price
            })

            if sold_qty > 0:
                revenue = sold_qty * random.randint(12000, 30000)
                self.revenues.append({
                    "date": (datetime.now() - timedelta(days=random.randint(0, 20))).date(),
                    "type": "Bán thuốc",
                    "amount": revenue,
                    "doctor": "Kho thuốc"
                })

    def setup_ui(self):
        # Tiêu đề
        title = tk.Label(self.root, text="BẢNG ĐIỀU KHIỂN ADMIN",
                         font=("Helvetica", 20, "bold"), bg="#f4f6f9", fg="#2c3e50")
        title.pack(pady=15)

        # Notebook - các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_revenue_tab()
        self.create_drug_tab()
        self.create_appointment_tab()
        self.create_doctor_progress_tab()

    def create_revenue_tab(self):
        tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.notebook.add(tab, text="Tổng Doanh Thu")

        total = sum(r["amount"] for r in self.revenues)
        tk.Label(tab, text=f"TỔNG DOANH THU: {total:,} VNĐ",
                 font=("Arial", 18, "bold"), fg="#27ae60", bg="#f4f6f9").pack(pady=30)

        revenue_by_type = {"Khám bệnh": 0, "Bán thuốc": 0}
        for r in self.revenues:
            revenue_by_type[r["type"]] += r["amount"]

        tk.Label(tab, text=f"• Doanh thu từ khám bệnh: {revenue_by_type['Khám bệnh']:,} VNĐ",
                 font=("Arial", 14), bg="#f4f6f9").pack(anchor="w", padx=120)
        tk.Label(tab, text=f"• Doanh thu từ bán thuốc: {revenue_by_type['Bán thuốc']:,} VNĐ",
                 font=("Arial", 14), bg="#f4f6f9").pack(anchor="w", padx=120)

    def create_drug_tab(self):
        tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.notebook.add(tab, text="Quản Lý Thuốc")

        tree = ttk.Treeview(tab, columns=("Tên", "Nhập", "Bán", "Tồn", "Giá bán"),
                            show="headings", height=15)
        tree.heading("Tên", text="Tên thuốc")
        tree.heading("Nhập", text="Số lượng nhập")
        tree.heading("Bán", text="Đã bán")
        tree.heading("Tồn", text="Tồn kho")
        tree.heading("Giá bán", text="Giá bán (VNĐ)")

        tree.column("Tên", width=230)
        tree.column("Nhập", width=110, anchor="center")
        tree.column("Bán", width=110, anchor="center")
        tree.column("Tồn", width=110, anchor="center")
        tree.column("Giá bán", width=130, anchor="e")

        for drug in self.drugs:
            tree.insert("", "end", values=(
                drug["name"],
                drug["import_qty"],
                drug["sold_qty"],
                drug["stock"],
                f"{drug['sell_price']:,}"
            ))
        tree.pack(padx=20, pady=20, fill="both", expand=True)

        total_stock = sum(d["stock"] for d in self.drugs)
        tk.Label(tab, text=f"TỔNG TỒN KHO: {total_stock} hộp/viên",
                 font=("Arial", 12, "bold"), bg="#f4f6f9").pack(pady=5)

    def create_appointment_tab(self):
        tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.notebook.add(tab, text="Danh Sách Lịch Hẹn")

        # Bộ lọc
        filter_frame = tk.Frame(tab, bg="#f4f6f9")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Lọc theo trạng thái:", bg="#f4f6f9").pack(side="left", padx=5)
        self.status_filter = ttk.Combobox(filter_frame,
                                          values=["Tất cả", "Đã khám xong", "Đã xác nhận",
                                                  "Đang chờ xác nhận", "Đã hủy"], width=20)
        self.status_filter.set("Tất cả")
        self.status_filter.pack(side="left", padx=5)
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.load_appointments())

        # Treeview lịch hẹn
        self.tree_app = ttk.Treeview(tab,
                                     columns=("Thời gian", "Bệnh nhân", "Bác sĩ", "Trạng thái", "Phí khám"),
                                     show="headings", height=18)
        for col in self.tree_app["columns"]:
            self.tree_app.heading(col, text=col)
            self.tree_app.column(col, width=150, anchor="center")
        self.tree_app.column("Bệnh nhân", width=180)
        self.tree_app.column("Thời gian", width=160)

        self.tree_app.pack(padx=20, pady=10, fill="both", expand=True)
        self.load_appointments()

    def load_appointments(self):
        for item in self.tree_app.get_children():
            self.tree_app.delete(item)

        status = self.status_filter.get()
        for app in sorted(self.appointments, key=lambda x: x["time"], reverse=True):
            if status == "Tất cả" or app["status"] == status:
                self.tree_app.insert("", "end", values=(
                    app["time"].strftime("%d/%m/%Y %H:%M"),
                    app["patient"],
                    app["doctor"],
                    app["status"],
                    f"{app['fee']:,}" if app["fee"] > 0 else "-"
                ))

    def create_doctor_progress_tab(self):
        tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.notebook.add(tab, text="Tiến Độ Bác Sĩ")

        tk.Label(tab, text="SỐ BỆNH NHÂN ĐÃ KHÁM THEO NGÀY",
                 font=("Arial", 14, "bold"), bg="#f4f6f9").pack(pady=15)

        tree = ttk.Treeview(tab, columns=("Bác sĩ", "Ngày", "Số bệnh nhân"),
                            show="headings", height=18)
        tree.heading("Bác sĩ", text="Bác sĩ")
        tree.heading("Ngày", text="Ngày khám")
        tree.heading("Số bệnh nhân", text="Số bệnh nhân")

        tree.column("Bác sĩ", width=220)
        tree.column("Ngày", width=150, anchor="center")
        tree.column("Số bệnh nhân", width=150, anchor="center")

        doctor_stats = {}
        for app in self.appointments:
            if app["status"] == "Đã khám xong":
                doc = app["doctor"]
                date = app["time"].date()
                doctor_stats.setdefault(doc, {}).setdefault(date, 0)
                doctor_stats[doc][date] += 1

        for doc, dates in doctor_stats.items():
            for date, count in dates.items():
                tree.insert("", "end", values=(doc, date.strftime("%d/%m/%Y"), count))

        tree.pack(padx=20, pady=10, fill="both", expand=True)


# ====================== CHẠY CHƯƠNG TRÌNH ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = ClinicReportApp(root)
    root.mainloop()