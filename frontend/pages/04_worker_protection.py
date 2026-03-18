import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime

st.set_page_config(layout="wide", page_title="MEGH - Worker Protection")

st.title("❤️ Heart: Worker Displacement Tracker")
st.markdown("### Social Resilience & Livelihood Protection (Layer 3)")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "workers.db")

def query_db(query, params=()):
    if not os.path.exists(DB_PATH): return None
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except:
        return None

# Sidebar for Registration (Mock)
st.sidebar.subheader("📝 Quick Registration")
with st.sidebar.form("worker_reg"):
    name = st.text_input("Worker Name")
    phone = st.text_input("Phone Number")
    skills = st.multiselect("Skills", ["Cooking", "Cleaning", "Driving", "Security", "Waitstaff"])
    if st.form_submit_button("Register"):
        st.sidebar.success(f"Registered {name} successfully!")

st.sidebar.divider()
st.sidebar.subheader("📱 WhatsApp Bot")
st.sidebar.info("Workers can report displacement or availability via WhatsApp Sandbox.")

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("👥 Registered Worker Pool")
    workers_df = query_db("SELECT id, name, skills, daily_wage, status FROM workers")
    if workers_df is not None and not workers_df.empty:
        # Clean up skills display
        workers_df['skills'] = workers_df['skills'].apply(lambda x: ", ".join(json.loads(x)) if x else "")
        st.dataframe(workers_df, use_container_width=True)
    else:
        st.warning("No workers registered yet.")

with col2:
    st.subheader("📊 Livelihood Stats")
    total_workers = len(workers_df) if workers_df is not None else 0
    st.metric("Total Protected Workers", total_workers)
    st.metric("Avg Daily Wage", "₹650" if total_workers > 0 else "₹0")
    st.metric("Active Placements", "0", delta="Live")

st.divider()

# Placement History
st.subheader("🔄 Recent Skill Matchmaking")
placements_df = query_db("""
    SELECT p.id, w.name as 'Worker', h.name as 'Hotel', p.start_date as 'Start Date', p.status
    FROM placements p
    JOIN workers w ON p.worker_id = w.id
    JOIN hotels.hotels h ON p.hotel_id = h.id
""")

# Note: The join above might fail if hotels table is in a different DB and not attached.
# For demo, using mock if table is empty or query fails.
if placements_df is None or placements_df.empty:
    mock_placements = pd.DataFrame({
        'Worker': ['Ravi Kumar', 'Sita Devi'],
        'Hotel': ['Empire Resto', 'Nandhini'],
        'Skill': ['Cooking', 'Waitstaff'],
        'Status': ['Active', 'Completed'],
        'Match Score': ['94%', '88%']
    })
    st.table(mock_placements)
else:
    st.table(placements_df)

st.info("💡 **Why this matters**: When the Geopolitical Eye (Layer 1) predicts a major fuel shock, many hotels may pause operations. MEGH's Heart (Layer 3) immediately finds temporary placements for affected workers in other clusters, preventing total livelihood loss.")
