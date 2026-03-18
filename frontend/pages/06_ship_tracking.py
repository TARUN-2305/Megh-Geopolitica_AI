import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
import sqlite3
import os
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(layout="wide", page_title="MEGH - Global Ship Tracking")

st.title("🚢 Wisdom: Global Shipping & Chokepoints")
st.markdown("### Monitoring Energy Supply Lines (Layer 1 Analysis)")

# Project root setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "ships.db")

def load_ship_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # Get latest positions for each ship
        df = pd.read_sql_query("""
            SELECT * FROM ship_positions 
            WHERE timestamp IN (SELECT MAX(timestamp) FROM ship_positions GROUP BY mmsi)
        """, conn)
    except Exception as e:
        st.error(f"Error loading ships: {e}")
        df = pd.DataFrame()
    conn.close()
    return df

st.sidebar.subheader("🌍 Chokepoint Focus")
focus = st.sidebar.selectbox("Jump to Region:", [
    "Global View",
    "Strait of Hormuz", 
    "Babal-Mandeb (Red Sea)", 
    "Suez Canal", 
    "Malacca Strait"
])

# Chokepoint coordinates
REGIONS = {
    "Global View": {"lat": 20.0, "lng": 60.0, "zoom": 3},
    "Strait of Hormuz": {"lat": 26.58, "lng": 56.25, "zoom": 8},
    "Babal-Mandeb (Red Sea)": {"lat": 12.60, "lng": 43.33, "zoom": 8},
    "Suez Canal": {"lat": 30.00, "lng": 32.50, "zoom": 8},
    "Malacca Strait": {"lat": 1.45, "lng": 102.80, "zoom": 7}
}

df_ships = load_ship_data()

col_map, col_details = st.columns([3, 1])

with col_map:
    center = REGIONS[focus]
    m = folium.Map(location=[center['lat'], center['lng']], zoom_start=center['zoom'], tiles="CartoDB dark_matter")
    
    if not df_ships.empty:
        marker_cluster = MarkerCluster(name="Active Vessels").add_to(m)
        
        for _, row in df_ships.iterrows():
            popup_text = f"""
            <b>{row['ship_name']}</b><br>
            MMSI: {row['mmsi']}<br>
            Speed: {row['speed']} kn<br>
            Course: {row['course']}°<br>
            Region: {row['chokepoint']}<br>
            Last Reported: {row['timestamp'][:16]}
            """
            
            folium.Marker(
                location=[row['lat'], row['lng']],
                popup=folium.Popup(popup_text, max_width=200),
                icon=folium.Icon(color='blue', icon='ship', prefix='fa')
            ).add_to(marker_cluster)
            
        # Add a heatmap for density
        HeatMap(data=df_ships[['lat', 'lng']].values, radius=15, blur=10, name="Vessel Density").add_to(m)
        
    st_folium(m, width=900, height=600)

with col_details:
    st.subheader("📊 Fleet Statistics")
    if not df_ships.empty:
        st.metric("Total Vessels Tracked", len(df_ships))
        
        # Breakdown by chokepoint
        counts = df_ships['chokepoint'].value_counts()
        st.write("**Activity by Region:**")
        for region, count in counts.items():
            st.write(f"- {region}: {count}")
            
        st.divider()
        st.subheader("⚠️ Alerts")
        # Simulate some alerts
        if focus == "Strait of Hormuz":
            st.error("🚨 **High Traffic Density**: Above average tanker presence near Qeshm Island.")
        elif focus == "Babal-Mandeb (Red Sea)":
            st.warning("⚠️ **Logistics Lag**: Vessels in northbound transit showing 15% speed reduction.")
        else:
            st.info("No active shipping alerts for this region.")
    else:
        st.warning("No live AIS data available. Run the ship tracker agent to populate.")
        if st.button("🚀 Trigger Ship Tracker Agent"):
            subprocess_path = os.path.join(BASE_DIR, "agents", "ship_tracker", "run.py")
            import subprocess
            subprocess.run(["python", subprocess_path])
            st.rerun()

st.divider()
st.info("💡 **Demo Context**: This data reflects Layer 1's 'Geopolitical Eye'. By monitoring ship density and speed variations in these chokepoints, MEGH can predict supply shocks before they reach Bengaluru market prices.")
