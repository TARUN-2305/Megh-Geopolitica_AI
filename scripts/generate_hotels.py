import random
import sqlite3
import os
from faker import Faker

# Project root setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "hotels.db")

fake = Faker('en_IN')  # Indian locale for realistic names

# Bengaluru approximate bounding box
LAT_MIN, LAT_MAX = 12.85, 13.10
LON_MIN, LON_MAX = 77.45, 77.75

# Ward names for context
wards = ['Malleswaram', 'Jayanagar', 'Indiranagar', 'Whitefield', 
         'Koramangala', 'HSR Layout', 'Rajajinagar', 'Basavanagudi']

def generate_hotels(count=75):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS hotels')
    c.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ward TEXT,
            lat REAL,
            lng REAL,
            cuisine TEXT,
            lpg_stock INTEGER,
            lpg_capacity INTEGER,
            last_updated TIMESTAMP
        )
    ''')

    for _ in range(count):
        name = fake.company() + " Hotel"
        ward = random.choice(wards)
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lng = random.uniform(LON_MIN, LON_MAX)
        cuisine = random.choice(['South Indian', 'North Indian', 'Chinese', 'Multi-cuisine'])
        stock = random.randint(0, 10)
        capacity = random.randint(10, 20)
        
        c.execute('''
            INSERT INTO hotels (name, ward, lat, lng, cuisine, lpg_stock, lpg_capacity, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (name, ward, lat, lng, cuisine, stock, capacity))

    conn.commit()
    conn.close()
    print(f"✅ {count} hotels added to {DB_PATH}.")

if __name__ == "__main__":
    generate_hotels()
