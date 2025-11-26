import tkinter as tk
from config.settings import APP_TITLE, WINDOW_SIZE
from database.models import ClinicDatabase
from core.auth import AuthManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class ClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # Khởi tạo Database và Auth
        self.db = ClinicDatabase()
        self.auth = AuthManager(self.db)
        
        self.show_login_window()

    def show_login_window(self):
        self.clear_window()
        LoginWindow(self, self)

    def show_main_window(self):
        self.clear_window()
        MainWindow(self, self)

    def logout(self):
        self.auth.logout()
        self.show_login_window()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()