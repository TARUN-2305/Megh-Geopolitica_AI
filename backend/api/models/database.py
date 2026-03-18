import sqlite3
import os
from datetime import datetime

# Path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "predictions.db")

def update_predictions(predictions):
    """Store predictions in SQLite"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS ward_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward TEXT,
            probability REAL,
            date DATE,
            UNIQUE(ward, date)
        )
    ''')
    
    for pred in predictions:
        c.execute('''
            INSERT OR REPLACE INTO ward_predictions (ward, probability, date)
            VALUES (?, ?, ?)
        ''', (pred['ward'], pred['probability'], pred['date']))
    
    conn.commit()
    conn.close()
