import tkinter as tk
from tkinter import ttk

class ReportsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="BÁO CÁO THỐNG KÊ", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Thực hiện Query đếm trực tiếp
        cursor = self.controller.db.cursor
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='patient'")
        total_patients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='doctor'")
        total_doctors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medicines")
        total_medicines = cursor.fetchone()[0]
        
        stats_frame = ttk.Frame(self)
        stats_frame.pack(pady=20)
        
        ttk.Label(stats_frame, text=f"Tổng số bệnh nhân: {total_patients}", font=("Arial", 12)).pack(pady=5, anchor="w")
        ttk.Label(stats_frame, text=f"Tổng số bác sĩ: {total_doctors}", font=("Arial", 12)).pack(pady=5, anchor="w")
        ttk.Label(stats_frame, text=f"Tổng số lịch hẹn: {total_appointments}", font=("Arial", 12)).pack(pady=5, anchor="w")
        ttk.Label(stats_frame, text=f"Tổng số loại thuốc: {total_medicines}", font=("Arial", 12)).pack(pady=5, anchor="w")