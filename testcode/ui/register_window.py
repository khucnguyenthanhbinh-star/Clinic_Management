# ui/register_window.py
# Tương tự login, nhưng cho đăng ký
from tkinter import ttk
from core.utils import clear_screen
from core.auth import register
from ui.login_window import create_login_screen

def create_register_screen(app):
    clear_screen(app.root)
    
    frame = ttk.Frame(app.root, padding="50")
    frame.place(relx=0.5, rely=0.5, anchor="center")
    
    ttk.Label(frame, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
    
    ttk.Label(frame, text="Tên đăng nhập:").grid(row=1, column=0, pady=10, sticky="e")
    username_entry = ttk.Entry(frame, width=25)
    username_entry.grid(row=1, column=1, pady=10)
    
    ttk.Label(frame, text="Mật khẩu:").grid(row=2, column=0, pady=10, sticky="e")
    password_entry = ttk.Entry(frame, width=25, show="*")
    password_entry.grid(row=2, column=1, pady=10)
    
    ttk.Label(frame, text="Họ tên:").grid(row=3, column=0, pady=10, sticky="e")
    name_entry = ttk.Entry(frame, width=25)
    name_entry.grid(row=3, column=1, pady=10)
    
    def do_register():
        username = username_entry.get()
        password = password_entry.get()
        name = name_entry.get()
        if username and password and name:
            if register(app, username, password, name):
                create_login_screen(app)
        else:
            from core.utils import show_error
            show_error("Vui lòng điền đầy đủ thông tin!")
    
    ttk.Button(frame, text="Đăng ký", command=do_register).grid(row=4, column=0, columnspan=2, pady=20)
    ttk.Button(frame, text="Quay lại", command=lambda: create_login_screen(app)).grid(row=5, column=0, columnspan=2)