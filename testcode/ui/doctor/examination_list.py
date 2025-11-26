import tkinter as tk
from tkinter import ttk

class ExaminationListView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ttk.Label(self, text="DANH SÁCH KHÁM", font=("Arial", 16, "bold")).pack(pady=20)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20)
        
        tree = ttk.Treeview(tree_frame, columns=("patient", "date", "time", "reason"), show="headings")
        tree.heading("patient", text="Bệnh nhân")
        tree.heading("date", text="Ngày")
        tree.heading("time", text="Giờ")
        tree.heading("reason", text="Lý do")
        
        # Lấy tất cả lịch hẹn
        appointments = self.controller.db.get_appointments()
        
        for apt in appointments:
            # Lấy tên bệnh nhân từ username
            patient_user = self.controller.db.get_user(apt["patient"])
            patient_name = patient_user["name"] if patient_user else apt["patient"]
            
            tree.insert("", "end", values=(patient_name, apt["date"], apt["time"], apt["reason"]))
        
        tree.pack(fill="both", expand=True)