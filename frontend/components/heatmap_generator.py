import folium
from folium.plugins import MarkerCluster
import sqlite3
import pandas as pd
import os
import streamlit as st

# Project root setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "hotels.db")

def create_hotel_map(center=[12.97, 77.59], zoom=12):
    """Creates a Folium map with hotel clusters and status indicators"""
    if not os.path.exists(DB_PATH):
        return folium.Map(location=center, zoom_start=zoom)
        
    # Fetch hotels from DB
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM hotels", conn)
    except Exception as e:
        print(f"Error reading hotels DB: {e}")
        conn.close()
        return folium.Map(location=center, zoom_start=zoom)
    conn.close()
    
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB dark_matter")
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, row in df.iterrows():
        # Color based on stock level
        stock_ratio = row['lpg_stock'] / row['lpg_capacity']
        if stock_ratio < 0.2:
            color = 'red'
            status_text = "🔴 URGENT"
        elif stock_ratio < 0.5:
            color = 'orange'
            status_text = "🟡 LOW"
        else:
            color = 'green'
            status_text = "🟢 OK"
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; color: #333; width: 200px;">
            <h4 style="margin: 0 0 5px 0;">{row['name']}</h4>
            <p style="margin: 0; font-size: 12px;"><b>Ward:</b> {row['ward']}</p>
            <p style="margin: 0; font-size: 12px;"><b>Cuisine:</b> {row['cuisine']}</p>
            <p style="margin: 10px 0 5px 0;"><b>LPG Stock:</b> {row['lpg_stock']}/{row['lpg_capacity']}</p>
            <p style="margin: 0; font-size: 14px;"><b>Status:</b> {status_text}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon='cutlery', prefix='fa')
        ).add_to(marker_cluster)
    
    return m
