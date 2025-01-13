import tkinter as tk
from tkinter import ttk

import psutil

from db.db import create_database, insert_load_data, fetch_history


class SystemMonitor:
    def __init__(self, root: tk.Tk, db_path: str):
        self.root = root
        self.root.title("System Monitor")

        self.history_button = tk.Button(root, text="История", command=self.show_history)
        self.history_button.place(relx=1.0, rely=0.0, anchor='ne')

        self.top_label = tk.Label(root, text="Уровень загруженности\n", font=("Helvetica", 16))
        self.top_label.pack(pady=(40, 0))

        self.cpu_label = tk.Label(root, text="Загрузка ЦП: 0%", font=("Helvetica", 16))
        self.cpu_label.pack(pady=10)

        self.ram_label = tk.Label(root, text="Использование ОЗУ: 0%", font=("Helvetica", 16))
        self.ram_label.pack(pady=10)

        self.disk_label = tk.Label(root, text="Использование ПЗУ: 0%", font=("Helvetica", 16))
        self.disk_label.pack(pady=10)

        self.record_button = tk.Button(root, text="Начать запись", command=self.toggle_recording)
        self.record_button.pack(pady=10)

        self.timer_label = tk.Label(root, text="Время записи: 00:00", font=("Helvetica", 16))
        self.timer_label.pack(pady=10)

        self.recording = False
        self.elapsed_time = 0
        self.quantity_record = 0
        self.db_path = db_path

        self.update_metrics()

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title('История Записи')

        tree = ttk.Treeview(history_window, columns=("id","timestamp", "cpu_usage", "ram_usage", "disk_usage"), show='headings')
        tree.heading("id", text="№")
        tree.heading("timestamp", text="Время")
        tree.heading("cpu_usage", text="Загрузка ЦП (%)")
        tree.heading("ram_usage", text="Загрузка ОЗУ (%)")
        tree.heading("disk_usage", text="Загрузка ПЗУ (%)")

        sorted_records = sorted(fetch_history(self.quantity_record, self.db_path), key=lambda record: record[0])

        for record in sorted_records:
            tree.insert("", tk.END, values=tuple(record))

        tree.pack(expand=True, fill='both')

        return history_window

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.quantity_record = 0
        self.recording = True
        self.record_button.config(text="Остановить запись")
        self.update_timer()

    def stop_recording(self):
        self.recording = False
        self.record_button.config(text="Начать запись")

    def update_timer(self):
        if self.recording:
            self.elapsed_time = self.elapsed_time + 1
            minutes, seconds = divmod(self.elapsed_time, 60)
            self.timer_label.config(text=f"Время записи: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)
        else:
            self.elapsed_time = 0
            minutes, seconds = divmod(self.elapsed_time, 60)
            self.timer_label.config(text=f"Время записи: {minutes:02}:{seconds:02}")

    def update_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        self.cpu_label.config(text=f"Загрузка ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"Использование ОЗУ: {ram_usage}%")
        self.disk_label.config(text=f"Использование ПЗУ: {disk_usage}%")

        if self.recording:
            insert_load_data(cpu_usage, ram_usage, disk_usage, self.db_path)
            self.quantity_record += 1

        self.root.after(1000, self.update_metrics)


if __name__ == "__main__":
    db_path = create_database('data.db')
    root = tk.Tk()
    app = SystemMonitor(db_path)
    root.mainloop()