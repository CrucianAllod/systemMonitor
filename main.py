import tkinter as tk

from GUI.system_monitor import SystemMonitor
from db.db import create_database


if __name__ == "__main__":
    db_path = create_database('data.db')
    root = tk.Tk()
    app = SystemMonitor(root, db_path)
    root.mainloop()