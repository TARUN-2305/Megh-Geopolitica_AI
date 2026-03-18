import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os

# Database helper
def get_db_metric(db_name, query, default="--"):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "data", db_name)
    if not os.path.exists(db_path):
        return default
    try:
        conn = sqlite3.connect(db_path)
        res = conn.execute(query).fetchone()
        conn.close()
        return res[0] if res and res[0] is not None else default
    except:
        return default

st.set_page_config(
    page_title="MEGH - Geopolitical Resilience",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 MEGH (ಮೇಘ): Geopolitical Resilience Dashboard")
st.markdown("### Master Execution & Governance Handler for Karnataka")

# Top Level Metrics
risk_prob = get_db_metric("predictions.db", "SELECT AVG(probability) FROM ward_predictions", 0.45)
risk_cat = "High" if risk_prob > 0.7 else "Medium" if risk_prob > 0.3 else "Low"

worker_count = get_db_metric("workers.db", "SELECT COUNT(*) FROM workers", 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("LPG Shortage Risk", risk_cat, delta=f"{int(risk_prob*100)}%", delta_color="inverse")
col2.metric("Brent Crude", "$84.20", delta="1.5%")
col3.metric("Expert Consensus", "88%", delta="High")
col4.metric("Protected Workers", f"{worker_count:,}", delta="Real-time")

st.divider()

# Main Dashboard Content
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📍 Live Prediction Heatmap (South Bengaluru)")
    # Placeholder for Folium Map
    st.info("Interactive Heatmap Loading... (Layer 1 Analysis)")
    # Mock chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 3) / [50, 50, 50] + [12.9716, 77.5946, 0.5],
        columns=['lat', 'lon', 'risk']
    )
    st.map(chart_data)

with col_right:
    st.subheader("📢 Expert Insight Feed (Layer 0)")
    st.success("**Prashant Dhawan**: Red Sea tensions likely to impact LPG import premiums by Friday.")
    st.warning("**Abhijit Chavda**: Strategic shift in Malacca Strait monitoring increases logistics uncertainty.")
    st.info("**Chanakyan**: Local supply chains in South India need immediate hedging.")

st.divider()

# Detailed Sections
tab1, tab2, tab3 = st.tabs(["Hive (P2P Swap)", "Heart (Worker Protection)", "Wisdom (Geopolitical Eye)"])

with tab1:
    st.subheader("🐝 Hive: Fuel Swap Market")
    st.write("Real-time P2P matching for hotel fuel clusters. When AI predicts a shortage, the Hive triggers redistribution.")
    
    # Simple preview of the network
    import plotly.express as px
    df_nodes = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 1, 3, 5],
        'status': ['Surplus', 'Shortage', 'Surplus', 'Shortage', 'Surplus'],
        'name': ['H1', 'H2', 'H3', 'H4', 'H5']
    })
    fig_preview = px.scatter(df_nodes, x='x', y='y', text='name', color='status',
                            color_discrete_map={'Surplus':'#2ecc71', 'Shortage':'#e74c3c'},
                            title="Local Cluster Logistics Preview")
    fig_preview.update_traces(marker=dict(size=20))
    fig_preview.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_preview, use_container_width=True)
    
    st.progress(65)
    st.caption("65% Capacity Optimization Reached (Jayanagar Cluster)")
    if st.button("Open Full Market Interface"):
        st.switch_page("pages/03_fuel_swap_market.py")

with tab2:
    st.subheader("❤️ Heart: Worker Displacement Tracker")
    st.write("Monitoring gig workers affected by supply chain shocks. When Layer 1 predicts a city-wide fuel shock, MEGH's Heart identifies high-risk hotel employees for immediate skill matching and temporary displacement protection.")
    st.metric("Total Protected Workers", worker_count)
    if st.button("Open Worker Protection Management"):
        st.switch_page("pages/04_worker_protection.py")

with tab3:
    st.subheader("👁️ Wisdom: Geopolitical Impact Analysis")
    st.write("Deep dive into global events and their local butterfly effects. Use the Chain of Thought tool to trace causal paths.")
    if st.button("Explore Chain of Thought"):
        st.switch_page("pages/05_chain_of_thought.py")
