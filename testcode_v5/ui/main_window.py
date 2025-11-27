import tkinter as tk
from tkinter import ttk


from ui.patient import book_appointment, view_appointments, medical_records, update_info, payment, patient_dashboard
from ui.doctor import examination_list, examination, patient_records
from ui.admin import manage_doctors, manage_patients, manage_appointments, manage_medicines, manage_users, reports


class MainWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Lấy thông tin user
        username = self.controller.auth.current_user
        user_data = self.controller.db.get_user(username)
        display_name = user_data['name'] if user_data else "Unknown"
        
        # --- TOP BAR ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Xin chào: {display_name}", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(top_frame, text="Đăng xuất", command=self.controller.logout).pack(side="right")
        
        # --- CONTAINER CHÍNH ---
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # MENU BÊN TRÁI
        menu_frame = ttk.LabelFrame(container, text="Menu", width=200)
        menu_frame.pack(side="left", fill="y", padx=5)
        menu_frame.pack_propagate(False)
        
        # KHUNG NỘI DUNG BÊN PHẢI (Nơi hiển thị các màn hình)
        self.content_frame = ttk.Frame(container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Tạo menu
        self.create_menu(menu_frame)

        # --- TỰ ĐỘNG HIỂN THỊ TRANG CHỦ (DASHBOARD) ---
        # Thay vì để trắng, ta load Dashboard ngay lập tức
        if self.controller.auth.current_role == "patient":
            self.switch_view(patient_dashboard.PatientDashboardView)
        elif self.controller.auth.current_role == "doctor":
            # Nếu có dashboard bác sĩ thì load, tạm thời load danh sách khám
            self.switch_view(examination_list.ExaminationListView)
        elif self.controller.auth.current_role == "admin":
            self.switch_view(reports.ReportsView)

    def create_menu(self, parent):
        role = self.controller.auth.current_role
        
        if role == "patient":
            # Thêm nút Trang chủ vào menu
            self.add_btn(parent, "Trang chủ", lambda: self.switch_view(patient_dashboard.PatientDashboardView))
            self.add_btn(parent, "Đặt lịch hẹn", lambda: self.switch_view(book_appointment.BookAppointmentView))
            self.add_btn(parent, "Quản lý lịch hẹn", lambda: self.switch_view(view_appointments.ViewAppointmentsView))
            self.add_btn(parent, "Lịch sử khám", lambda: self.switch_view(medical_records.MedicalRecordsView))
            self.add_btn(parent, "Thanh toán", lambda: self.switch_view(payment.PaymentView))
            self.add_btn(parent, "Cập nhật Hồ sơ", lambda: self.switch_view(update_info.UpdateInfoView))
        
        elif role == "doctor":
            self.add_btn(parent, "Danh sách khám", lambda: self.switch_view(examination_list.ExaminationListView))
            self.add_btn(parent, "Khám bệnh", lambda: self.switch_view(examination.ExaminationView))
            self.add_btn(parent, "Tra cứu hồ sơ BN", lambda: self.switch_view(patient_records.PatientRecordsView))

        elif role == "admin":
            self.add_btn(parent, "Báo cáo thống kê", lambda: self.switch_view(reports.ReportsView))
            self.add_btn(parent, "Quản lý bác sĩ", lambda: self.switch_view(manage_doctors.ManageDoctorsView))
            self.add_btn(parent, "Quản lý bệnh nhân", lambda: self.switch_view(manage_patients.ManagePatientsView))
            self.add_btn(parent, "Quản lý lịch hẹn", lambda: self.switch_view(manage_appointments.ManageAppointmentsView))
            self.add_btn(parent, "Quản lý kho thuốc", lambda: self.switch_view(manage_medicines.ManageMedicinesView))
            self.add_btn(parent, "Quản lý tài khoản", lambda: self.switch_view(manage_users.ManageUsersView))

    def add_btn(self, parent, text, command):
        btn = ttk.Button(parent, text=text, command=command)
        btn.pack(fill="x", pady=2)

    def switch_view(self, view_class):
        # Xóa màn hình hiện tại
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Tạo và hiển thị màn hình mới
        view_class(self.content_frame, self.controller).pack(fill="both", expand=True)