# ui/patient/patient_dashboard.py
from tkinter import ttk
from ui.patient.book_appointment import show_book_appointment
from ui.patient.view_appointments import show_my_appointments
from ui.patient.medical_records import show_medical_history
from ui.patient.update_info import show_update_info  # Giả sử có file này
from ui.patient.payment import show_payment  # Giả sử có file này

def create_patient_menu(app, parent):
    ttk.Button(parent, text="Đặt lịch hẹn", command=lambda: show_book_appointment(app)).pack(fill="x", pady=2)
    ttk.Button(parent, text="Xem lịch hẹn", command=lambda: show_my_appointments(app)).pack(fill="x", pady=2)
    ttk.Button(parent, text="Lịch sử khám", command=lambda: show_medical_history(app)).pack(fill="x", pady=2)
    ttk.Button(parent, text="Cập nhật thông tin", command=lambda: show_update_info(app)).pack(fill="x", pady=2)
    ttk.Button(parent, text="Thanh toán", command=lambda: show_payment(app)).pack(fill="x", pady=2)