#!/usr/bin/env python3
"""
REAL data collector agent
Fetches news from GDELT and NewsAPI
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Use absolute paths for the database to ensure it works from any location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "raw", "events.db")

load_dotenv(os.path.join(BASE_DIR, ".env"))

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
GDELT_URL = "http://api.gdeltproject.org/api/v2/doc/doc"

def fetch_gdelt_events():
    """Fetch recent geopolitical events from GDELT"""
    params = {
        'query': '(conflict OR tension OR blockade OR sanction) AND (oil OR gas OR energy)',
        'mode': 'artlist',
        'format': 'json',
        'timespan': '24h',
        'maxrecords': 100
    }
    
    try:
        response = requests.get(GDELT_URL, params=params, timeout=10)
        data = response.json()
        
        events = []
        for article in data.get('articles', []):
            events.append({
                'title': article['title'],
                'source': article['domain'],
                'date': article['seendate'],
                'url': article['url'],
                'type': 'geopolitical',
                'raw_data': json.dumps(article)
            })
        
        return events
    except Exception as e:
        print(f"GDELT error: {e}")
        return []

def fetch_newsapi():
    """Fetch from NewsAPI as backup"""
    if not NEWSAPI_KEY or "your_newsapi_key_here" in NEWSAPI_KEY:
        print("NewsAPI key not configured correctly.")
        return []
    
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'oil OR gas OR LPG OR shortage',
        'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'sortBy': 'relevancy',
        'language': 'en',
        'apiKey': NEWSAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'error':
            print(f"NewsAPI error: {data.get('message')}")
            return []
            
        events = []
        for article in data.get('articles', []):
            events.append({
                'title': article['title'],
                'source': article['source']['name'],
                'date': article['publishedAt'],
                'url': article['url'],
                'type': 'news',
                'raw_data': json.dumps(article)
            })
        
        return events
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []

def store_events(events):
    """Save events to database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            date TIMESTAMP,
            url TEXT,
            type TEXT,
            processed INTEGER DEFAULT 0,
            raw_data TEXT,
            UNIQUE(url)
        )
    ''')
    
    count = 0
    for event in events:
        try:
            c.execute('''
                INSERT OR IGNORE INTO events (title, source, date, url, type, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event['title'], event['source'], event['date'], 
                  event['url'], event['type'], event['raw_data']))
            if c.rowcount > 0:
                count += 1
        except:
            continue
    
    conn.commit()
    conn.close()
    print(f"Stored {count} new events in {DB_PATH}")

def run_data_collector():
    print(f"[{datetime.now()}] Data collector cycle starting...")
    
    # Fetch from multiple sources
    gdelt_events = fetch_gdelt_events()
    newsapi_events = fetch_newsapi()
    
    all_events = gdelt_events + newsapi_events
    
    if all_events:
        store_events(all_events)
        print(f"✅ Finished collection cycle")
    else:
        print("⚠️ No new events found this cycle")
    
    # Trigger predictor agent module-style if needed
    # However, for the demo orchestrator, we want independent threads.
    # So we don't trigger subprocess here when running as a module.

if __name__ == "__main__":
    run_data_collector()
