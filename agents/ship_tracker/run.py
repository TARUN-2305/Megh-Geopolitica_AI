"""
MEGH Ship Tracker Agent
Fetches vessel positions near critical chokepoints.
Supports MarineTraffic API and a fallback mock for demo purposes.
"""

import sys
import os
import requests
import sqlite3
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add base directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv('MARINETRAFFIC_API_KEY')
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "ships.db")

# Critical Chokepoints
CHOKEPOINTS = {
    "Strait of Hormuz": {"lat": 26.58, "lng": 56.25, "radius": 1.5},
    "Babal-Mandeb (Red Sea)": {"lat": 12.60, "lng": 43.33, "radius": 1.0},
    "Suez Canal": {"lat": 30.00, "lng": 32.50, "radius": 0.8},
    "Malacca Strait": {"lat": 1.45, "lng": 102.80, "radius": 2.0}
}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ship_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mmsi INTEGER,
            ship_name TEXT,
            lat REAL,
            lng REAL,
            speed REAL,
            course REAL,
            chokepoint TEXT,
            timestamp TIMESTAMP,
            UNIQUE(mmsi, timestamp)
        )
    ''')
    conn.commit()
    conn.close()

def fetch_real_ais():
    """Placeholder for real MarineTraffic API integration"""
    if not API_KEY or "your_marinetraffic_key" in API_KEY:
        return []
    
    # Real API call logic would go here
    # url = f'https://services.marinetraffic.com/api/exportvessels/{API_KEY}/timespan:20/protocol:json'
    return []

def generate_mock_ais():
    """Generates mock AIS data for demo purposes"""
    ships = []
    ship_prefixes = ["MT", "MV", "Gas", "Ocean", "Global", "Arctic", "Pacific"]
    ship_suffixes = ["Explorer", "Voyager", "Leader", "Star", "Queen", "Titan", "Carrier"]
    
    for name, coords in CHOKEPOINTS.items():
        # Generate 5-10 ships per chokepoint
        num_ships = random.randint(5, 12)
        for i in range(num_ships):
            # Random offset from center
            lat_off = random.uniform(-coords['radius'], coords['radius'])
            lng_off = random.uniform(-coords['radius'], coords['radius'])
            
            ship_name = f"{random.choice(ship_prefixes)} {random.choice(ship_suffixes)} {random.randint(10, 99)}"
            mmsi = random.randint(200000000, 700000000)
            
            ships.append({
                'mmsi': mmsi,
                'ship_name': ship_name,
                'lat': coords['lat'] + lat_off,
                'lng': coords['lng'] + lng_off,
                'speed': round(random.uniform(5, 20), 1),
                'course': random.randint(0, 359),
                'chokepoint': name,
                'timestamp': datetime.now().isoformat()
            })
    return ships

def store_ships(ships):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    count = 0
    for ship in ships:
        try:
            c.execute('''
                INSERT OR IGNORE INTO ship_positions (mmsi, ship_name, lat, lng, speed, course, chokepoint, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ship['mmsi'], ship['ship_name'], ship['lat'], ship['lng'], 
                  ship['speed'], ship['course'], ship['chokepoint'], ship['timestamp']))
            if c.rowcount > 0:
                count += 1
        except:
            continue
            
    # Cleanup old data (keep last 24h)
    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    c.execute("DELETE FROM ship_positions WHERE timestamp < ?", (yesterday,))
    
    conn.commit()
    conn.close()
    print(f"Stored {count} ship positions in {DB_PATH}")

def run_ship_tracker():
    print(f"[{datetime.now()}] Ship Tracker started...")
    init_db()
    
    # Try real AIS first
    ships = fetch_real_ais()
    
    # Fallback to mock for demo if no real data
    if not ships:
        print("  No real data found/API key missing. Generating mock data for demo...")
        ships = generate_mock_ais()
        
    if ships:
        store_ships(ships)
        print(f"✅ Finished ship tracking cycle")

if __name__ == "__main__":
    run_ship_tracker()
