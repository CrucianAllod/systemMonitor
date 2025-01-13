import os
import sqlite3
from datetime import datetime
from typing import List, Tuple


def create_database(db_name: str) -> str:
    db_directory = os.path.dirname(__file__)
    db_path = os.path.join(db_directory, db_name)
    connection = sqlite3.connect(db_path)
    print(f"Creating database at: {db_path}")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SystemLoad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DateTime NOT NULL,
        cpu_usage REAL NOT NULL,
        ram_usage REAL NOT NULL,
        disk_usage REAL NOT NULL
    )
    """)

    connection.commit()
    connection.close()

    return db_path

def insert_load_data(cpu_usage: float, ram_usage: float, disk_usage: float, db_path: str) -> None:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO SystemLoad (timestamp, cpu_usage, ram_usage, disk_usage)
    VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cpu_usage, ram_usage, disk_usage))

    connection.commit()
    connection.close()

def fetch_history(quantity_record: int, db_path: str) -> List[Tuple[int, str, float, float, float]]:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM SystemLoad ORDER BY timestamp DESC LIMIT ?""", (quantity_record,))

    history = cursor.fetchall()

    connection.close()

    return history
