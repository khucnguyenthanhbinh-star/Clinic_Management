import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class ReportsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # === TOP SECTION ===
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(top_frame, text="BÁO CÁO THỐNG KÊ", font=("Arial", 16, "bold")).pack(side="left")
        
        ttk.Button(top_frame, text="Làm mới", command=self.refresh_report).pack(side="right", padx=5)
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(self, text="Thống kê chung", padding=15)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        cursor = self.controller.db.cursor
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='patient'")
        total_patients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='doctor'")
        total_doctors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medicines")
        total_medicines = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Hoan thanh'")
        completed_appointments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid'")
        unpaid_invoices = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM invoices WHERE status = 'Paid'")
        paid_amount = cursor.fetchone()[0] or 0
        
        # Main stats - 2x4 grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="both", expand=True)
        
        stats_data = [
            ("👥 Tổng bệnh nhân", total_patients, "blue"),
            ("👨‍⚕️ Tổng bác sĩ", total_doctors, "green"),
            ("📅 Tổng lịch hẹn", total_appointments, "orange"),
            ("✅ Lịch hẹn hoàn thành", completed_appointments, "darkgreen"),
            ("💊 Loại thuốc", total_medicines, "purple"),
            ("💰 Hóa đơn chưa thanh toán", unpaid_invoices, "red"),
            ("💵 Tổng doanh thu", f"{paid_amount:,} đ", "darkgreen"),
            ("📊 Tỷ lệ hoàn thành", f"{(completed_appointments*100//total_appointments if total_appointments > 0 else 0)}%", "blue"),
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            row = i // 4
            col = i % 4
            
            stat_frame = ttk.Frame(stats_grid, relief="solid", borderwidth=1)
            stat_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            ttk.Label(stat_frame, text=label, font=("Arial", 10)).pack(padx=10, pady=(8, 2))
            ttk.Label(stat_frame, text=str(value), font=("Arial", 14, "bold")).pack(padx=10, pady=(2, 8))
        
        # Configure grid weights for responsiveness
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        for i in range(2):
            stats_grid.rowconfigure(i, weight=1)
        
        # === DETAIL SECTION ===
        detail_frame = ttk.LabelFrame(self, text="Chi tiết theo ngày", padding=10)
        detail_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Date range selector
        filter_frame = ttk.Frame(detail_frame)
        filter_frame.pack(fill="x", pady=10)
        
        ttk.Label(filter_frame, text="Từ ngày:").pack(side="left", padx=5)
        
        today = datetime.now()
        start_date_default = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date_default = today.strftime("%Y-%m-%d")
        
        self.start_date_var = tk.StringVar(value=start_date_default)
        start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=15)
        start_date_entry.pack(side="left", padx=5)
        
        ttk.Label(filter_frame, text="Đến ngày:").pack(side="left", padx=5)
        self.end_date_var = tk.StringVar(value=end_date_default)
        end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=15)
        end_date_entry.pack(side="left", padx=5)
        
        ttk.Button(filter_frame, text="Tìm", command=self.filter_by_date).pack(side="left", padx=5)
        
        # Appointments by date
        apt_frame = ttk.LabelFrame(detail_frame, text="Lịch hẹn", padding=5)
        apt_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.apt_tree = ttk.Treeview(apt_frame, columns=("date", "count", "completed"), show="headings", height=6)
        self.apt_tree.heading("date", text="Ngày")
        self.apt_tree.heading("count", text="Tổng lịch hẹn")
        self.apt_tree.heading("completed", text="Hoàn thành")
        
        self.apt_tree.column("date", width=150)
        self.apt_tree.column("count", width=150)
        self.apt_tree.column("completed", width=150)
        
        apt_scrollbar = ttk.Scrollbar(apt_frame, orient="vertical", command=self.apt_tree.yview)
        self.apt_tree.configure(yscroll=apt_scrollbar.set)
        
        self.apt_tree.pack(side="left", fill="both", expand=True)
        apt_scrollbar.pack(side="right", fill="y")
        
        # Revenue by date
        revenue_frame = ttk.LabelFrame(detail_frame, text="Doanh thu", padding=5)
        revenue_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.revenue_tree = ttk.Treeview(revenue_frame, columns=("date", "total", "paid"), show="headings", height=6)
        self.revenue_tree.heading("date", text="Ngày")
        self.revenue_tree.heading("total", text="Tổng hóa đơn (đ)")
        self.revenue_tree.heading("paid", text="Đã thanh toán (đ)")
        
        self.revenue_tree.column("date", width=150)
        self.revenue_tree.column("total", width=150)
        self.revenue_tree.column("paid", width=150)
        
        revenue_scrollbar = ttk.Scrollbar(revenue_frame, orient="vertical", command=self.revenue_tree.yview)
        self.revenue_tree.configure(yscroll=revenue_scrollbar.set)
        
        self.revenue_tree.pack(side="left", fill="both", expand=True)
        revenue_scrollbar.pack(side="right", fill="y")
        
        self.refresh_report()
    
    def refresh_report(self):
        """Làm mới báo cáo"""
        # Reset to default dates
        today = datetime.now()
        self.start_date_var.set((today - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.end_date_var.set(today.strftime("%Y-%m-%d"))
        
        self.filter_by_date()
    
    def filter_by_date(self):
        """Lọc dữ liệu theo ngày"""
        try:
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            
            if start_date > end_date:
                messagebox.showwarning("Thông báo", "Ngày bắt đầu không được sau ngày kết thúc")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ (YYYY-MM-DD)")
            return
        
        # Clear trees
        for item in self.apt_tree.get_children():
            self.apt_tree.delete(item)
        for item in self.revenue_tree.get_children():
            self.revenue_tree.delete(item)
        
        cursor = self.controller.db.cursor
        
        # Get appointments by date
        cursor.execute("""
            SELECT date, 
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'Hoan thanh' THEN 1 ELSE 0 END) as completed
            FROM appointments
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date DESC
        """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        apt_rows = cursor.fetchall()
        for row in apt_rows:
            self.apt_tree.insert("", "end", values=(row[0], row[1], row[2]))
        
        # Get revenue by date
        cursor.execute("""
            SELECT DATE(created_at) as date,
                   COUNT(*) as total_invoices,
                   SUM(amount) as total_amount,
                   SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END) as paid_amount
            FROM invoices
            WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        revenue_rows = cursor.fetchall()
        for row in revenue_rows:
            total = row[2] or 0
            paid = row[3] or 0
            self.revenue_tree.insert("", "end", values=(row[0], f"{int(total):,}", f"{int(paid):,}"))