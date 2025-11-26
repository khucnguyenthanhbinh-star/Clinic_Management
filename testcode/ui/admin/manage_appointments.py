import tkinter as tk
from tkinter import ttk

class ManageAppointmentsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="QUẢN LÝ LỊCH HẸN", font=("Arial", 16, "bold")).pack(pady=20)
        tree = ttk.Treeview(self, columns=("patient", "date", "time", "reason", "status"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("reason", text="Lý do")
        tree.heading("status", text="Trạng thái")
        
        appointments = self.controller.db.get_appointments()
        
        for apt in appointments:
            patient_user = self.controller.db.get_user(apt["patient"])
            patient_name = patient_user["name"] if patient_user else apt["patient"]
            tree.insert("", "end", values=(patient_name, apt["date"], apt["time"], apt["reason"], apt["status"]))
            
        tree.pack(fill="both", expand=True, padx=20)