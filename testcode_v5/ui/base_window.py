# ui/base_window.py
from tkinter import ttk
from config.settings import WINDOW_TITLE, WINDOW_SIZE

class ClinicManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.current_user = None
        self.current_role = None
        self.content_frame = None  # Sẽ được set trong main_window