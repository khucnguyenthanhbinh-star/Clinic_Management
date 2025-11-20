import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os


def load_patients_from_csv():
    patients = []
    csv_file = "users.csv"
    if not os.path.exists(csv_file):
        messagebox.showerror("Lỗi", f"Không tìm thấy file '{csv_file}'!\nVui lòng đặt file cùng thư mục.")
        return patients

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get('status', '').strip().lower()
                if any(k in status for k in ['chờ', 'đang chờ']):
                    patients.append({
                        'id': int(row['id']),
                        'name': row['name'].strip(),
                        'phone': row['phone'].strip(),
                        'email': row['email'].strip() if row['email'].strip() else None,
                        'status': row['status'].strip()
                    })
    except Exception as e:
        messagebox.showerror("Lỗi đọc file", f"Không thể đọc CSV:\n{str(e)}")
    return patients

class NotificationService:
    def __init__(self):
        self.templates = {
            "Mời đến quầy thanh toán": "Mời bệnh nhân {name} đến quầy thanh toán.",
            "Bác sĩ sẵn sàng": "Bác sĩ đã sẵn sàng. Mời bệnh nhân {name} vào phòng khám số {room}.",
            "Mang giấy tờ": "Mời bệnh nhân {name} mang theo CMND/CCCD đến quầy lễ tân.",
            "Kết quả đã có": "Kết quả xét nghiệm của bệnh nhân {name} đã có. Mời đến quầy nhận.",
            "Hóa đơn thanh toán": "Hóa đơn của bệnh nhân {name} đã in xong. Mời thanh toán."
        }

    def send(self, patient, message, channel):
        name = patient['name']
        full_msg = message.replace("{name}", name)
        if "{room}" in full_msg:
            full_msg = full_msg.replace("{room}", "1")

    
        print(f"[{channel.upper()}] → {name}: {full_msg}")
        return True, f"[{datetime.now().strftime('%H:%M:%S')}] → BN {patient['id']}: [{channel.upper()}] {full_msg}"


class NotificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GỬI THÔNG BÁO - LỄ TÂN")
        self.root.geometry("860x640")
        self.root.configure(bg="#f4f6f9")

        self.service = NotificationService()
        self.setup_ui()
        self.load_patients()

    def setup_ui(self):
       
        header = tk.Frame(self.root, bg="#2c3e50", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="GỬI THÔNG BÁO CHO BỆNH NHÂN", font=("Helvetica", 18, "bold"),
                 bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=15)

        main = tk.Frame(self.root, bg="#f4f6f9")
        main.pack(fill="both", expand=True, padx=20, pady=15)

    
        left_frame = tk.Frame(main, bg="white", relief="ridge", bd=2)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_frame, text="BỆNH NHÂN ĐANG CHỜ (từ users.csv)", font=("Arial", 13, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=10)

        self.listbox = tk.Listbox(left_frame, font=("Arial", 11), selectbackground="#a8d5f2", height=18)
        self.listbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))

       
        tk.Button(left_frame, text="LÀM MỚI DANH SÁCH", bg="#3498db", fg="white",
                  command=self.load_patients).pack(pady=5)

        right_frame = tk.Frame(main, bg="white", relief="ridge", bd=2)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(right_frame, text="SOẠN THÔNG BÁO", font=("Arial", 13, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=10)

        tk.Label(right_frame, text="Mẫu nhanh:", bg="white").pack(anchor="w", padx=20, pady=(10, 3))
        self.template_combo = ttk.Combobox(right_frame, state="readonly", width=45)
        self.template_combo['values'] = list(self.service.templates.keys())
        self.template_combo.pack(padx=20, pady=3)
        self.template_combo.bind("<<ComboboxSelected>>", self.apply_template)

     
        tk.Label(right_frame, text="Nội dung thông báo:", bg="white").pack(anchor="w", padx=20, pady=(10, 3))
        self.text_msg = tk.Text(right_frame, height=7, width=50, font=("Arial", 11), wrap="word")
        self.text_msg.pack(padx=20, pady=3)

       
        tk.Label(right_frame, text="Kênh gửi:", bg="white").pack(anchor="w", padx=20, pady=(10, 3))
        self.channel_var = tk.StringVar(value="app")
        channel_frame = tk.Frame(right_frame, bg="white")
        channel_frame.pack(anchor="w", padx=20)
        tk.Radiobutton(channel_frame, text="App", variable=self.channel_var, value="app", bg="white").pack(side="left")
        tk.Radiobutton(channel_frame, text="SMS", variable=self.channel_var, value="sms", bg="white").pack(side="left", padx=15)
        tk.Radiobutton(channel_frame, text="Email", variable=self.channel_var, value="email", bg="white").pack(side="left")

    
        tk.Button(right_frame, text="GỬI THÔNG BÁO", bg="#27ae60", fg="white",
                  font=("Arial", 12, "bold"), command=self.send, height=2).pack(pady=15)

       
        tk.Label(right_frame, text="Lịch sử gửi:", bg="white").pack(anchor="w", padx=20, pady=(10, 3))
        self.log_text = tk.Text(right_frame, height=6, font=("Courier", 9), bg="#f8f9fa", state="disabled")
        self.log_text.pack(fill="x", padx=20, pady=3)

    def load_patients(self):
        self.listbox.delete(0, tk.END)
        self.patients = load_patients_from_csv()
        if not self.patients:
            self.listbox.insert(tk.END, "Không có bệnh nhân đang chờ")
            return
        for p in self.patients:
            self.listbox.insert(tk.END, f"{p['name']} - {p['status']}")

    def apply_template(self, event=None):
        key = self.template_combo.get()
        if key in self.service.templates:
            self.text_msg.delete(1.0, tk.END)
            self.text_msg.insert(tk.END, self.service.templates[key])

    def send(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn bệnh nhân!")
            return

        patient = self.patients[sel[0]]
        message = self.text_msg.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Trống", "Vui lòng nhập nội dung thông báo!")
            return

        channel = self.channel_var.get()
        success, log = self.service.send(patient, message, channel)

        if success:
            messagebox.showinfo("Thành công", "Đã gửi thông báo!")
            self.add_to_log(log)
        else:
            messagebox.showerror("Lỗi", "Gửi thất bại!")

    def add_to_log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = NotificationApp(root)
    root.mainloop()
