import tkinter as tk
from tkinter import ttk

# Import các giao diện con
# Lưu ý: Đảm bảo tên file trong thư mục ui/patient, ui/doctor... khớp với lệnh import
from ui.patient import book_appointment, view_appointments, medical_records, update_info, payment
from ui.doctor import examination_list, examination, prescription, patient_records
from ui.admin import manage_doctors, manage_patients, manage_appointments, manage_medicines, manage_users, reports
# Nếu bạn đã tách file receptionist thì import lẻ, nếu chưa thì giữ nguyên cách cũ
# Dưới đây là import theo cấu trúc đã tách file:
from ui.receptionist import create_invoice, send_notification 
# Nếu lỗi import receptionist, hãy kiểm tra lại file trong thư mục ui/receptionist

class MainWindow(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # --- SỬA LỖI TẠI ĐÂY ---
        # Code cũ: user_data = self.controller.db.users[self.controller.auth.current_user]
        # Code mới: Gọi hàm get_user từ DB
        username = self.controller.auth.current_user
        user_data = self.controller.db.get_user(username)
        
        # Top bar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Kiểm tra user_data có tồn tại không để tránh lỗi NoneType
        display_name = user_data['name'] if user_data else "Unknown"
        
        ttk.Label(top_frame, text=f"Xin chào: {display_name}", font=("Arial", 12)).pack(side="left")
        ttk.Button(top_frame, text="Đăng xuất", command=self.controller.logout).pack(side="right")
        
        # Container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Menu
        menu_frame = ttk.LabelFrame(container, text="Menu", width=200)
        menu_frame.pack(side="left", fill="y", padx=5)
        menu_frame.pack_propagate(False)
        
        # Content Area
        self.content_frame = ttk.Frame(container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.create_menu(menu_frame)

    def create_menu(self, parent):
        role = self.controller.auth.current_role
        
        if role == "patient":
            self.add_btn(parent, "Đặt lịch hẹn", lambda: self.switch_view(book_appointment.BookAppointmentView))
            self.add_btn(parent, "Quản lý lịch hẹn", lambda: self.switch_view(view_appointments.ViewAppointmentsView))
            self.add_btn(parent, "Lịch sử khám", lambda: self.switch_view(medical_records.MedicalRecordsView))
            self.add_btn(parent, "Cập nhật TT", lambda: self.switch_view(update_info.UpdateInfoView))
            self.add_btn(parent, "Thanh toán", lambda: self.switch_view(payment.PaymentView))
        
        elif role == "doctor":
            self.add_btn(parent, "Danh sách khám", lambda: self.switch_view(examination_list.ExaminationListView))
            self.add_btn(parent, "Khám bệnh", lambda: self.switch_view(examination.ExaminationView))
            self.add_btn(parent, "Kê đơn thuốc", lambda: self.switch_view(prescription.PrescriptionView))
            self.add_btn(parent, "Xem hồ sơ BN", lambda: self.switch_view(patient_records.PatientRecordsView))

        elif role == "admin":
            self.add_btn(parent, "Quản lý bác sĩ", lambda: self.switch_view(manage_doctors.ManageDoctorsView))
            self.add_btn(parent, "Quản lý bệnh nhân", lambda: self.switch_view(manage_patients.ManagePatientsView))
            self.add_btn(parent, "Quản lý lịch hẹn", lambda: self.switch_view(manage_appointments.ManageAppointmentsView))
            self.add_btn(parent, "Quản lý kho thuốc", lambda: self.switch_view(manage_medicines.ManageMedicinesView))
            self.add_btn(parent, "Quản lý tài khoản", lambda: self.switch_view(manage_users.ManageUsersView))
            self.add_btn(parent, "Xem báo cáo", lambda: self.switch_view(reports.ReportsView))

        elif role == "receptionist":
            # Dùng lại view đặt lịch của patient nhưng với vai trò lễ tân
            self.add_btn(parent, "Đăng ký lịch hẹn", lambda: self.switch_view(book_appointment.BookAppointmentView))
            self.add_btn(parent, "Quản lý lịch hẹn", lambda: self.switch_view(manage_appointments.ManageAppointmentsView))
            self.add_btn(parent, "Tạo hóa đơn", lambda: self.switch_view(create_invoice.CreateInvoiceView))
            self.add_btn(parent, "Gửi thông báo", lambda: self.switch_view(send_notification.SendNotificationView))

    def add_btn(self, parent, text, command):
        ttk.Button(parent, text=text, command=command).pack(fill="x", pady=2)

    def switch_view(self, view_class):
        # Xóa nội dung cũ
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Tạo view mới
        view_class(self.content_frame, self.controller).pack(fill="both", expand=True)