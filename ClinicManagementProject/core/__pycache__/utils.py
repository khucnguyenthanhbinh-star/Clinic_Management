
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()