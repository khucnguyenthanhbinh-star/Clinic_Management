# Code đầy đủ hệ thống thông báo cho bác sĩ
# Bao gồm: tạo DB, tạo bảng, thêm thông báo, cập nhật trạng thái, UI hiển thị

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "hospital.db"

# ------------------------- TẠO DATABASE + BẢNG ---------------------------
def init_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            content TEXT,
            time TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

# ------------------------- HÀM THÊM THÔNG BÁO ---------------------------
def add_notification(doctor_id, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notifications (doctor_id, content, time, status) VALUES (?,?,?,?)",
              (doctor_id, content, time, "Chưa đọc"))

    conn.commit()
    conn.close()

# ------------------------- UI THÔNG BÁO BÁC SĨ ---------------------------
class DoctorNotifications:
    def __init__(self, root, doctor_id):
        self.root = root
        self.root.title("Thông báo cho bác sĩ")
        self.doctor_id = doctor_id

        # Bảng hiển thị thông báo
        self.tree = ttk.Treeview(root, columns=("id", "content", "time", "status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("content", text="Nội dung")
        self.tree.heading("time", text="Thời gian")
        self.tree.heading("status", text="Trạng thái")
        self.tree.column("id", width=40)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Nút đánh dấu đã đọc
        btn = tk.Button(root, text="Đánh dấu đã đọc", command=self.mark_read)
        btn.pack(pady=5)

        self.load_notifications()

    # Load thông báo từ DB
    def load_notifications(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("SELECT id, content, time, status FROM notifications WHERE doctor_id=? ORDER BY time DESC", (self.doctor_id,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    # Đánh dấu 1 thông báo là Đã đọc
    def mark_read(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một thông báo!")
            return

        notif_id = self.tree.item(selected[0])["values"][0]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE notifications SET status='Đã đọc' WHERE id=?", (notif_id,))
        conn.commit()
        conn.close()

        self.load_notifications()
        messagebox.showinfo("Thành công", "Đã cập nhật trạng thái!")

# ------------------------- CHẠY TEST ---------------------------
if __name__ == "__main__":
    init_database()

    # Test thêm thông báo mẫu
    add_notification(1, "Có lịch hẹn mới với bệnh nhân A")
    add_notification(1, "Hệ thống đã cập nhật thuốc mới")

    root = tk.Tk()
    app = DoctorNotifications(root, doctor_id=1)
    root.mainloop()
