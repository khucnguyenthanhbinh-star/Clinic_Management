import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

class Patient:
    """Class đại diện cho bệnh nhân"""
    def __init__(self, patient_id, name, dob, gender, phone, address, medical_history=""):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob
        self.gender = gender
        self.phone = phone
        self.address = address
        self.medical_history = medical_history
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'dob': self.dob,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'medical_history': self.medical_history,
            'created_date': self.created_date
        }

class PatientManager:
    """Class quản lý danh sách bệnh nhân"""
    def __init__(self):
        self.patients = {}
    
    def add_patient(self, patient):
        """Thêm bệnh nhân mới"""
        if patient.patient_id in self.patients:
            return False, "Mã bệnh nhân đã tồn tại"
        self.patients[patient.patient_id] = patient
        return True, "Thêm bệnh nhân thành công"
    
    def update_patient(self, patient):
        """Cập nhật thông tin bệnh nhân"""
        if patient.patient_id not in self.patients:
            return False, "Không tìm thấy bệnh nhân"
        self.patients[patient.patient_id] = patient
        return True, "Cập nhật thành công"
    
    def delete_patient(self, patient_id):
        """Xóa bệnh nhân"""
        if patient_id in self.patients:
            del self.patients[patient_id]
            return True, "Xóa thành công"
        return False, "Không tìm thấy bệnh nhân"
    
    def search_patient(self, keyword):
        """Tìm kiếm bệnh nhân theo tên hoặc mã"""
        results = []
        for patient in self.patients.values():
            if keyword.lower() in patient.name.lower() or keyword in patient.patient_id:
                results.append(patient)
        return results
    
    def get_all_patients(self):
        """Lấy tất cả bệnh nhân"""
        return list(self.patients.values())

class PatientRecordGUI:
    """Class giao diện quản lý hồ sơ bệnh nhân"""
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý hồ sơ bệnh nhân")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        self.manager = PatientManager()
        self.selected_patient_id = None
        
        self.create_widgets()
        self.load_sample_data()
    
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="HỒ SƠ BỆNH NHÂN", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Form nhập liệu
        left_frame = tk.LabelFrame(main_container, text="Thông tin bệnh nhân", 
                                  font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Mã bệnh nhân
        tk.Label(left_frame, text="Mã bệnh nhân:", font=('Arial', 10), bg='white').grid(row=0, column=0, sticky='w', pady=8)
        self.entry_id = tk.Entry(left_frame, font=('Arial', 10), width=30)
        self.entry_id.grid(row=0, column=1, pady=8, padx=10)
        
        # Họ tên
        tk.Label(left_frame, text="Họ và tên:", font=('Arial', 10), bg='white').grid(row=1, column=0, sticky='w', pady=8)
        self.entry_name = tk.Entry(left_frame, font=('Arial', 10), width=30)
        self.entry_name.grid(row=1, column=1, pady=8, padx=10)
        
        # Ngày sinh
        tk.Label(left_frame, text="Ngày sinh:", font=('Arial', 10), bg='white').grid(row=2, column=0, sticky='w', pady=8)
        self.entry_dob = tk.Entry(left_frame, font=('Arial', 10), width=30)
        self.entry_dob.grid(row=2, column=1, pady=8, padx=10)
        tk.Label(left_frame, text="(dd/mm/yyyy)", font=('Arial', 8), fg='gray', bg='white').grid(row=2, column=2, sticky='w')
        
        # Giới tính
        tk.Label(left_frame, text="Giới tính:", font=('Arial', 10), bg='white').grid(row=3, column=0, sticky='w', pady=8)
        self.gender_var = tk.StringVar(value="Nam")
        gender_frame = tk.Frame(left_frame, bg='white')
        gender_frame.grid(row=3, column=1, sticky='w', pady=8, padx=10)
        tk.Radiobutton(gender_frame, text="Nam", variable=self.gender_var, value="Nam", 
                      font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(gender_frame, text="Nữ", variable=self.gender_var, value="Nữ", 
                      font=('Arial', 10), bg='white').pack(side=tk.LEFT)
        
        # Số điện thoại
        tk.Label(left_frame, text="Số điện thoại:", font=('Arial', 10), bg='white').grid(row=4, column=0, sticky='w', pady=8)
        self.entry_phone = tk.Entry(left_frame, font=('Arial', 10), width=30)
        self.entry_phone.grid(row=4, column=1, pady=8, padx=10)
        
        # Địa chỉ
        tk.Label(left_frame, text="Địa chỉ:", font=('Arial', 10), bg='white').grid(row=5, column=0, sticky='w', pady=8)
        self.entry_address = tk.Entry(left_frame, font=('Arial', 10), width=30)
        self.entry_address.grid(row=5, column=1, pady=8, padx=10)
        
        # Tiền sử bệnh
        tk.Label(left_frame, text="Tiền sử bệnh:", font=('Arial', 10), bg='white').grid(row=6, column=0, sticky='nw', pady=8)
        self.text_history = tk.Text(left_frame, font=('Arial', 10), width=30, height=6)
        self.text_history.grid(row=6, column=1, pady=8, padx=10)
        
        # Buttons
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        tk.Button(button_frame, text="Thêm mới", command=self.add_patient, 
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cập nhật", command=self.update_patient, 
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Xóa", command=self.delete_patient, 
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Làm mới", command=self.clear_form, 
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Right panel - Danh sách bệnh nhân
        right_frame = tk.LabelFrame(main_container, text="Danh sách bệnh nhân", 
                                   font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Search bar
        search_frame = tk.Frame(right_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Tìm kiếm:", font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=5)
        self.entry_search = tk.Entry(search_frame, font=('Arial', 10), width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Tìm", command=self.search_patients, 
                 bg='#34495e', fg='white', font=('Arial', 9, 'bold'), 
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Hiển thị tất cả", command=self.load_all_patients, 
                 bg='#7f8c8d', fg='white', font=('Arial', 9, 'bold'), 
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(right_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Tên', 'Ngày sinh', 'Giới tính', 'SĐT', 'Địa chỉ'),
                                show='headings', yscrollcommand=scrollbar_y.set, 
                                xscrollcommand=scrollbar_x.set, height=15)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Định nghĩa các cột
        self.tree.heading('ID', text='Mã BN')
        self.tree.heading('Tên', text='Họ và tên')
        self.tree.heading('Ngày sinh', text='Ngày sinh')
        self.tree.heading('Giới tính', text='Giới tính')
        self.tree.heading('SĐT', text='Số điện thoại')
        self.tree.heading('Địa chỉ', text='Địa chỉ')
        
        self.tree.column('ID', width=80, anchor='center')
        self.tree.column('Tên', width=150)
        self.tree.column('Ngày sinh', width=100, anchor='center')
        self.tree.column('Giới tính', width=80, anchor='center')
        self.tree.column('SĐT', width=100, anchor='center')
        self.tree.column('Địa chỉ', width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind sự kiện double click
        self.tree.bind('<Double-1>', self.on_tree_select)
    
    def add_patient(self):
        """Thêm bệnh nhân mới"""
        # Validate
        if not self.validate_form():
            return
        
        patient = Patient(
            patient_id=self.entry_id.get().strip(),
            name=self.entry_name.get().strip(),
            dob=self.entry_dob.get().strip(),
            gender=self.gender_var.get(),
            phone=self.entry_phone.get().strip(),
            address=self.entry_address.get().strip(),
            medical_history=self.text_history.get('1.0', tk.END).strip()
        )
        
        success, message = self.manager.add_patient(patient)
        
        if success:
            messagebox.showinfo("Thành công", message)
            self.clear_form()
            self.load_all_patients()
        else:
            messagebox.showerror("Lỗi", message)
    
    def update_patient(self):
        """Cập nhật thông tin bệnh nhân"""
        if not self.selected_patient_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân để cập nhật")
            return
        
        if not self.validate_form():
            return
        
        patient = Patient(
            patient_id=self.entry_id.get().strip(),
            name=self.entry_name.get().strip(),
            dob=self.entry_dob.get().strip(),
            gender=self.gender_var.get(),
            phone=self.entry_phone.get().strip(),
            address=self.entry_address.get().strip(),
            medical_history=self.text_history.get('1.0', tk.END).strip()
        )
        
        success, message = self.manager.update_patient(patient)
        
        if success:
            messagebox.showinfo("Thành công", message)
            self.clear_form()
            self.load_all_patients()
        else:
            messagebox.showerror("Lỗi", message)
    
    def delete_patient(self):
        """Xóa bệnh nhân"""
        if not self.selected_patient_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân để xóa")
            return
        
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bệnh nhân này?")
        if confirm:
            success, message = self.manager.delete_patient(self.selected_patient_id)
            if success:
                messagebox.showinfo("Thành công", message)
                self.clear_form()
                self.load_all_patients()
            else:
                messagebox.showerror("Lỗi", message)
    
    def search_patients(self):
        """Tìm kiếm bệnh nhân"""
        keyword = self.entry_search.get().strip()
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm")
            return
        
        results = self.manager.search_patient(keyword)
        self.update_tree(results)
        
        if not results:
            messagebox.showinfo("Thông báo", "Không tìm thấy bệnh nhân nào")
    
    def load_all_patients(self):
        """Load tất cả bệnh nhân"""
        patients = self.manager.get_all_patients()
        self.update_tree(patients)
    
    def update_tree(self, patients):
        """Cập nhật danh sách trên treeview"""
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Thêm dữ liệu mới
        for patient in patients:
            self.tree.insert('', tk.END, values=(
                patient.patient_id,
                patient.name,
                patient.dob,
                patient.gender,
                patient.phone,
                patient.address
            ))
    
    def on_tree_select(self, event):
        """Xử lý sự kiện chọn bệnh nhân từ danh sách"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            patient_id = item['values'][0]
            
            patient = self.manager.patients.get(patient_id)
            if patient:
                self.selected_patient_id = patient_id
                self.fill_form(patient)
    
    def fill_form(self, patient):
        """Điền thông tin bệnh nhân vào form"""
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, patient.patient_id)
        
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, patient.name)
        
        self.entry_dob.delete(0, tk.END)
        self.entry_dob.insert(0, patient.dob)
        
        self.gender_var.set(patient.gender)
        
        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, patient.phone)
        
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, patient.address)
        
        self.text_history.delete('1.0', tk.END)
        self.text_history.insert('1.0', patient.medical_history)
    
    def clear_form(self):
        """Xóa dữ liệu trên form"""
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_dob.delete(0, tk.END)
        self.gender_var.set("Nam")
        self.entry_phone.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.text_history.delete('1.0', tk.END)
        self.selected_patient_id = None
    
    def validate_form(self):
        """Validate dữ liệu form"""
        if not self.entry_id.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập mã bệnh nhân")
            return False
        
        if not self.entry_name.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên")
            return False
        
        if not self.entry_dob.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập ngày sinh")
            return False
        
        if not self.entry_phone.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập số điện thoại")
            return False
        
        return True
    
    def load_sample_data(self):
        """Load dữ liệu mẫu"""
        sample_patients = [
            Patient("BN001", "Nguyễn Văn An", "15/03/1985", "Nam", "0901234567", "123 Láng Hạ, Đống Đa, Hà Nội", "Tiền sử: Tiểu đường type 2"),
            Patient("BN002", "Trần Thị Bình", "20/07/1992", "Nữ", "0912345678", "456 Giảng Võ, Ba Đình, Hà Nội", "Tiền sử: Huyết áp cao"),
            Patient("BN003", "Lê Hoàng Cường", "10/11/1978", "Nam", "0923456789", "789 Nguyễn Trãi, Thanh Xuân, Hà Nội", "Tiền sử: Viêm dạ dày"),
        ]
        
        for patient in sample_patients:
            self.manager.add_patient(patient)
        
        self.load_all_patients()

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientRecordGUI(root)
    root.mainloop()