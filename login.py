import tkinter as tk
from tkinter import ttk, messagebox
import csv
import hashlib
import os
from datetime import datetime

class AuthenticationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Xác thực")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        self.csv_file = "users.csv"
        self.current_user = None
        
        self.init_csv_file()
        
        self.show_login_screen()
    
    def init_csv_file(self):
        """Khởi tạo file CSV nếu chưa tồn tại"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'password_hash', 'name', 'email', 'phone', 'created_at'])
    
    def hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_user(self, username, password, name, email, phone):
        """Lưu thông tin người dùng vào CSV"""
        password_hash = self.hash_password(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, password_hash, name, email, phone, created_at])
    
    def check_user_exists(self, username):
        """Kiểm tra xem username đã tồn tại chưa"""
        if not os.path.exists(self.csv_file):
            return False
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return True
        return False
    
    def verify_user(self, username, password):
        """Xác thực thông tin đăng nhập"""
        password_hash = self.hash_password(password)
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password_hash'] == password_hash:
                    return row
        return None
    
    def delete_user(self, username):
        """Xóa tài khoản người dùng"""
        users = []
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] != username:
                    users.append(row)
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['username', 'password_hash', 'name', 'email', 'phone', 'created_at']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
    
    def get_user_info(self, username):
        """Lấy thông tin chi tiết của user"""
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return row
        return None
    
    def update_user_info(self, username, name=None, email=None, phone=None):
        """Cập nhật thông tin người dùng"""
        users = []
        
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    if name:
                        row['name'] = name
                    if email:
                        row['email'] = email
                    if phone:
                        row['phone'] = phone
                users.append(row)
        
        # Ghi lại file
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['username', 'password_hash', 'name', 'email', 'phone', 'created_at']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
    
    def clear_screen(self):
        """Xóa tất cả widget trên màn hình"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Hiển thị màn hình đăng nhập"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding="50")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = ttk.Label(main_frame, text="ĐĂNG NHẬP", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(main_frame, text="Tên đăng nhập:", 
                 font=("Arial", 11)).grid(row=1, column=0, pady=10, sticky="e", padx=(0, 10))
        username_entry = ttk.Entry(main_frame, width=25, font=("Arial", 11))
        username_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(main_frame, text="Mật khẩu:", 
                 font=("Arial", 11)).grid(row=2, column=0, pady=10, sticky="e", padx=(0, 10))
        password_entry = ttk.Entry(main_frame, width=25, show="●", font=("Arial", 11))
        password_entry.grid(row=2, column=1, pady=10)

        show_password = tk.BooleanVar()
        def toggle_password():
            if show_password.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="●")
        
        show_pass_check = ttk.Checkbutton(main_frame, text="Hiển thị mật khẩu", 
                                         variable=show_password, command=toggle_password)
        show_pass_check.grid(row=3, column=1, pady=5, sticky="w")
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return
            
            user = self.verify_user(username, password)
            if user:
                self.current_user = username
                messagebox.showinfo("Thành công", f"Chào mừng {user['name']}!")
                self.show_dashboard()
            else:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")
        
        login_btn = ttk.Button(main_frame, text="Đăng nhập", 
                              command=login, width=20)
        login_btn.grid(row=4, column=0, columnspan=2, pady=(20, 10))
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, 
                                                            sticky='ew', pady=20)
        
        register_label = ttk.Label(main_frame, text="Chưa có tài khoản?", 
                                  font=("Arial", 10))
        register_label.grid(row=6, column=0, columnspan=2, pady=(0, 5))
        
        register_btn = ttk.Button(main_frame, text="Đăng ký ngay", 
                                 command=self.show_register_screen, width=20)
        register_btn.grid(row=7, column=0, columnspan=2)
        
        password_entry.bind('<Return>', lambda e: login())
    
    def show_register_screen(self):
        """Hiển thị màn hình đăng ký"""
        self.clear_screen()

        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((250, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        form_frame = ttk.Frame(scrollable_frame, padding="30")
        form_frame.pack()
        
        title_label = ttk.Label(form_frame, text="ĐĂNG KÝ TÀI KHOẢN", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(form_frame, text="* Tên đăng nhập:", 
                 font=("Arial", 11)).grid(row=1, column=0, pady=10, sticky="e", padx=(0, 10))
        username_entry = ttk.Entry(form_frame, width=25, font=("Arial", 11))
        username_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(form_frame, text="* Mật khẩu:", 
                 font=("Arial", 11)).grid(row=2, column=0, pady=10, sticky="e", padx=(0, 10))
        password_entry = ttk.Entry(form_frame, width=25, show="●", font=("Arial", 11))
        password_entry.grid(row=2, column=1, pady=10)
        
        ttk.Label(form_frame, text="* Xác nhận mật khẩu:", 
                 font=("Arial", 11)).grid(row=3, column=0, pady=10, sticky="e", padx=(0, 10))
        confirm_password_entry = ttk.Entry(form_frame, width=25, show="●", font=("Arial", 11))
        confirm_password_entry.grid(row=3, column=1, pady=10)
        
        ttk.Label(form_frame, text="* Họ và tên:", 
                 font=("Arial", 11)).grid(row=4, column=0, pady=10, sticky="e", padx=(0, 10))
        name_entry = ttk.Entry(form_frame, width=25, font=("Arial", 11))
        name_entry.grid(row=4, column=1, pady=10)
        
        ttk.Label(form_frame, text="Email:", 
                 font=("Arial", 11)).grid(row=5, column=0, pady=10, sticky="e", padx=(0, 10))
        email_entry = ttk.Entry(form_frame, width=25, font=("Arial", 11))
        email_entry.grid(row=5, column=1, pady=10)
        
        ttk.Label(form_frame, text="Số điện thoại:", 
                 font=("Arial", 11)).grid(row=6, column=0, pady=10, sticky="e", padx=(0, 10))
        phone_entry = ttk.Entry(form_frame, width=25, font=("Arial", 11))
        phone_entry.grid(row=6, column=1, pady=10)
        
        note_label = ttk.Label(form_frame, text="* Trường bắt buộc", 
                              font=("Arial", 9), foreground="red")
        note_label.grid(row=7, column=0, columnspan=2, pady=(5, 0))
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            
            if not username or not password or not name:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ các trường bắt buộc!")
                return
            
            if len(username) < 3:
                messagebox.showerror("Lỗi", "Tên đăng nhập phải có ít nhất 3 ký tự!")
                return
            
            if len(password) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
                return
            
            if password != confirm_password:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            
            if self.check_user_exists(username):
                messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
                return
            
            self.save_user(username, password, name, email, phone)
            messagebox.showinfo("Thành công", "Đăng ký tài khoản thành công!\nVui lòng đăng nhập.")
            self.show_login_screen()
        
        register_btn = ttk.Button(form_frame, text="Đăng ký", 
                                 command=register, width=20)
        register_btn.grid(row=8, column=0, columnspan=2, pady=(20, 10))
        
        back_btn = ttk.Button(form_frame, text="Quay lại đăng nhập", 
                             command=self.show_login_screen, width=20)
        back_btn.grid(row=9, column=0, columnspan=2, pady=(0, 20))
    
    def show_dashboard(self):
        """Hiển thị dashboard sau khi đăng nhập"""
        self.clear_screen()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        user_info = self.get_user_info(self.current_user)
        welcome_label = ttk.Label(top_frame, 
                                 text=f"Xin chào, {user_info['name']}!", 
                                 font=("Arial", 14, "bold"))
        welcome_label.pack(side="left")
        
        logout_btn = ttk.Button(top_frame, text="Đăng xuất", 
                               command=self.logout)
        logout_btn.pack(side="right")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        info_frame = ttk.LabelFrame(main_frame, text="Thông tin tài khoản", padding="20")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        info_text = f"""
Tên đăng nhập: {user_info['username']}
Họ và tên: {user_info['name']}
Email: {user_info['email'] if user_info['email'] else 'Chưa cập nhật'}
Số điện thoại: {user_info['phone'] if user_info['phone'] else 'Chưa cập nhật'}
Ngày tạo: {user_info['created_at']}
        """
        
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=("Arial", 11), justify="left")
        info_label.pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        update_btn = ttk.Button(button_frame, text="Cập nhật thông tin", 
                               command=self.show_update_info, width=20)
        update_btn.grid(row=0, column=0, padx=10, pady=5)
        
        change_password_btn = ttk.Button(button_frame, text="Đổi mật khẩu", 
                                        command=self.show_change_password, width=20)
        change_password_btn.grid(row=0, column=1, padx=10, pady=5)
        
        delete_btn = ttk.Button(button_frame, text="Xóa tài khoản", 
                               command=self.confirm_delete_account, width=20)
        delete_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        # Warning
        warning_label = ttk.Label(main_frame, 
                                 text="⚠️ Xóa tài khoản sẽ xóa toàn bộ dữ liệu và không thể khôi phục", 
                                 foreground="red", font=("Arial", 9))
        warning_label.pack(pady=(0, 20))
    
    def show_update_info(self):
        """Hiển thị form cập nhật thông tin"""
        self.clear_screen()

        main_frame = ttk.Frame(self.root, padding="50")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = ttk.Label(main_frame, text="CẬP NHẬT THÔNG TIN", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        user_info = self.get_user_info(self.current_user)
        
        ttk.Label(main_frame, text="Họ và tên:", 
                 font=("Arial", 11)).grid(row=1, column=0, pady=10, sticky="e", padx=(0, 10))
        name_entry = ttk.Entry(main_frame, width=25, font=("Arial", 11))
        name_entry.insert(0, user_info['name'])
        name_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(main_frame, text="Email:", 
                 font=("Arial", 11)).grid(row=2, column=0, pady=10, sticky="e", padx=(0, 10))
        email_entry = ttk.Entry(main_frame, width=25, font=("Arial", 11))
        email_entry.insert(0, user_info['email'] if user_info['email'] else '')
        email_entry.grid(row=2, column=1, pady=10)
     
        ttk.Label(main_frame, text="Số điện thoại:", 
                 font=("Arial", 11)).grid(row=3, column=0, pady=10, sticky="e", padx=(0, 10))
        phone_entry = ttk.Entry(main_frame, width=25, font=("Arial", 11))
        phone_entry.insert(0, user_info['phone'] if user_info['phone'] else '')
        phone_entry.grid(row=3, column=1, pady=10)
        
        def update():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            
            if not name:
                messagebox.showerror("Lỗi", "Họ tên không được để trống!")
                return
            
            self.update_user_info(self.current_user, name, email, phone)
            messagebox.showinfo("Thành công", "Cập nhật thông tin thành công!")
            self.show_dashboard()

        update_btn = ttk.Button(main_frame, text="Cập nhật", 
                               command=update, width=15)
        update_btn.grid(row=4, column=0, pady=(20, 10))
        
        back_btn = ttk.Button(main_frame, text="Quay lại", 
                             command=self.show_dashboard, width=15)
        back_btn.grid(row=4, column=1, pady=(20, 10))
    
    def show_change_password(self):
        """Hiển thị form đổi mật khẩu"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, padding="50")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = ttk.Label(main_frame, text="ĐỔI MẬT KHẨU", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(main_frame, text="Mật khẩu hiện tại:", 
                 font=("Arial", 11)).grid(row=1, column=0, pady=10, sticky="e", padx=(0, 10))
        current_password_entry = ttk.Entry(main_frame, width=25, show="●", font=("Arial", 11))
        current_password_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(main_frame, text="Mật khẩu mới:", 
                 font=("Arial", 11)).grid(row=2, column=0, pady=10, sticky="e", padx=(0, 10))
        new_password_entry = ttk.Entry(main_frame, width=25, show="●", font=("Arial", 11))
        new_password_entry.grid(row=2, column=1, pady=10)
        
        ttk.Label(main_frame, text="Xác nhận mật khẩu:", 
                 font=("Arial", 11)).grid(row=3, column=0, pady=10, sticky="e", padx=(0, 10))
        confirm_password_entry = ttk.Entry(main_frame, width=25, show="●", font=("Arial", 11))
        confirm_password_entry.grid(row=3, column=1, pady=10)
        
        def change_password():
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()
            
            if not self.verify_user(self.current_user, current_password):
                messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!")
                return
            
            if len(new_password) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự!")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            
            users = []
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == self.current_user:
                        row['password_hash'] = self.hash_password(new_password)
                    users.append(row)
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['username', 'password_hash', 'name', 'email', 'phone', 'created_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)
            
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
            self.show_dashboard()
        
        change_btn = ttk.Button(main_frame, text="Đổi mật khẩu", 
                               command=change_password, width=15)
        change_btn.grid(row=4, column=0, pady=(20, 10))
        
        back_btn = ttk.Button(main_frame, text="Quay lại", 
                             command=self.show_dashboard, width=15)
        back_btn.grid(row=4, column=1, pady=(20, 10))
    
    def confirm_delete_account(self):
        """Xác nhận xóa tài khoản"""
        result = messagebox.askyesno(
            "Xác nhận xóa tài khoản",
            "Bạn có chắc chắn muốn xóa tài khoản?\n\n"
            "⚠️ Hành động này không thể hoàn tác!\n"
            "⚠️ Tất cả dữ liệu sẽ bị xóa vĩnh viễn!",
            icon='warning'
        )
        
        if result:
            self.show_confirm_password_dialog()
    
    def show_confirm_password_dialog(self):
        """Dialog nhập mật khẩu để xác nhận xóa tài khoản"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Xác nhận mật khẩu")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="30")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Nhập mật khẩu để xác nhận:", 
                 font=("Arial", 11)).pack(pady=(0, 10))
        
        password_entry = ttk.Entry(frame, width=30, show="●", font=("Arial", 11))
        password_entry.pack(pady=10)
        password_entry.focus()
        
        def confirm():
            password = password_entry.get()
            
            if self.verify_user(self.current_user, password):
                dialog.destroy()
                self.delete_user(self.current_user)
                messagebox.showinfo("Thành công", "Tài khoản đã được xóa!")
                self.current_user = None
                self.show_login_screen()
            else:
                messagebox.showerror("Lỗi", "Mật khẩu không đúng!")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        confirm_btn = ttk.Button(button_frame, text="Xác nhận", 
                                command=confirm, width=12)
        confirm_btn.pack(side="left", padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Hủy", 
                               command=dialog.destroy, width=12)
        cancel_btn.pack(side="left", padx=5)
        
        password_entry.bind('<Return>', lambda e: confirm())
    
    def logout(self):
        """Đăng xuất"""
        confirm = messagebox.askyesno("Xác nhận", "Bạn có muốn đăng xuất?")
        if confirm:
            self.current_user = None
            self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticationSystem(root)
    root.mainloop()