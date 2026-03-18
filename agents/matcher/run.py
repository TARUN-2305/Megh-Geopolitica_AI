import sys
import os
import time
import sqlite3
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.core.layer2_hive.matching_optimization import FuelSwapOptimizer

DB_PATH = os.path.join(BASE_DIR, "backend", "data", "hotels.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS swaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_hotel_id INTEGER,
            to_hotel_id INTEGER,
            cylinders INTEGER,
            distance_km REAL,
            timestamp TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def run_matcher():
    print(f"[{datetime.now()}] Matcher agent cycle starting...")
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    # Get hotels with potential surplus or demand
    # Surplus: stock > 8 and > 50% capacity (simple heuristic)
    # Demand: stock < 3
    hotels = []
    try:
        c = conn.cursor()
        c.execute("SELECT id, lat, lng, lpg_stock, lpg_capacity FROM hotels")
        rows = c.fetchall()
        
        optimizer = FuelSwapOptimizer()
        
        found_needs = False
        found_surplus = False
        
        for row in rows:
            hid, lat, lng, stock, capacity = row
            if stock < 3:
                optimizer.add_hotel(str(hid), (lat, lng), demand=3-stock, urgency=5 if stock == 0 else 3)
                found_needs = True
            elif stock > 10:
                optimizer.add_hotel(str(hid), (lat, lng), surplus=stock-8)
                found_surplus = True
        
        if found_needs and found_surplus:
            swaps = optimizer.solve()
            if swaps:
                print(f"Found {len(swaps)} optimal swaps!")
                for s in swaps:
                    c.execute('''
                        INSERT INTO swaps (from_hotel_id, to_hotel_id, cylinders, distance_km, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (s['from_hotel'], s['to_hotel'], s['cylinders'], s['distance_km'], datetime.now().isoformat()))
                conn.commit()
            else:
                print("No feasible swaps found this cycle.")
        else:
            print("Insufficient surplus or demand to run matching.")
            
    except Exception as e:
        print(f"Matcher Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    while True:
        run_matcher()
        time.sleep(60) # Run every minute for demo purposes
