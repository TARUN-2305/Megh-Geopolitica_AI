import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import pandas as pd
import sqlite3
import os
from streamlit_folium import st_folium
from frontend.api_client import get_api_client
from frontend.components.heatmap_generator import create_hotel_map

st.set_page_config(layout="wide", page_title="MEGH - Fuel Swap Market")

st.title("🐝 Hive: P2P Fuel Swap Market")
st.markdown("### Hyper-local Resilience via Resource Sharing (Layer 2)")

# Area Selection
col_select, col_stats = st.columns([1, 3])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "hotels.db")
PRED_DB_PATH = os.path.join(BASE_DIR, "backend", "data", "predictions.db")

def query_db(path, query, params=()):
    if not os.path.exists(path): return None
    try:
        conn = sqlite3.connect(path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# Standards for consistency
DEMAND_THRESHOLD = 3
TARGET_STOCK = 10
SURPLUS_THRESHOLD = 10

with col_select:
    ward = st.selectbox("Select Cluster Ward:", ["Jayanagar", "Indiranagar", "Malleswaram", "Whitefield"])
    
    # Real stats based on ward
    ward_hotels = query_db(DB_PATH, "SELECT * FROM hotels WHERE ward = ?", (ward,))
    num_hotels = len(ward_hotels) if not ward_hotels.empty else 0
    total_surplus = ward_hotels[ward_hotels['lpg_stock'] > SURPLUS_THRESHOLD]['lpg_stock'].sum() if num_hotels > 0 else 0
    total_demand = (TARGET_STOCK - ward_hotels[ward_hotels['lpg_stock'] < DEMAND_THRESHOLD]['lpg_stock']).sum() if num_hotels > 0 else 0

    # Prediction from predictions.db
    pred_df = query_db(PRED_DB_PATH, "SELECT probability FROM ward_predictions WHERE ward = ? ORDER BY date DESC LIMIT 1", (ward,))
    risk_prob = pred_df['probability'].iloc[0] if not pred_df.empty else 0.45

    st.metric("Active Hotels", num_hotels)
    st.metric("Total Surplus", f"{int(total_surplus)}")
    st.metric("Shortage Risk", f"{int(risk_prob*100)}%", delta=f"{int(total_demand)} units needed", delta_color="inverse")

with col_stats:
    # 1. Surplus/Demand Bar Chart (Aggregated from DB)
    ward_agg = query_db(DB_PATH, f"""
        SELECT ward, 
               SUM(CASE WHEN lpg_stock > {SURPLUS_THRESHOLD} THEN lpg_stock - {SURPLUS_THRESHOLD} ELSE 0 END) as surplus,
               SUM(CASE WHEN lpg_stock < {DEMAND_THRESHOLD} THEN {TARGET_STOCK} - lpg_stock ELSE 0 END) as demand
        FROM hotels GROUP BY ward
    """)
    
    if ward_agg is not None and not ward_agg.empty:
        fig_bars = go.Figure(data=[
            go.Bar(name='Surplus', x=ward_agg['ward'], y=ward_agg['surplus'], marker_color='#2ecc71'),
            go.Bar(name='Demand', x=ward_agg['ward'], y=ward_agg['demand'], marker_color='#e74c3c')
        ])
    else:
        fig_bars = go.Figure()
        
    fig_bars.update_layout(title="Cluster Resource Balance", barmode='group', template="plotly_dark")
    st.plotly_chart(fig_bars, use_container_width=True)

st.divider()

# --- Simulation Controls (for Demo) ---
st.sidebar.subheader("🛠️ Demo Controls")
if st.sidebar.button("🎲 Simulate Live Stock Changes"):
    conn = sqlite3.connect(DB_PATH) # Using global DB_PATH
    c = conn.cursor()
    
    # Get all hotels
    c.execute("SELECT id, lpg_stock, lpg_capacity FROM hotels")
    hotels = c.fetchall()
    
    # Decide how many hotels to update (10-15)
    num_to_update = random.randint(10, 15)
    hotel_ids = random.sample([h[0] for h in hotels], num_to_update)
    
    for hid in hotel_ids:
        # Fetch current stock
        c.execute("SELECT lpg_stock, lpg_capacity FROM hotels WHERE id = ?", (hid,))
        stock, cap = c.fetchone()
        
        # Decide type of change: create shortage or surplus?
        # Bias toward maintaining variety
        if stock < DEMAND_THRESHOLD:
            # Low stock – maybe give a small surplus to simulate delivery
            change = random.randint(1, 3)
        elif stock > cap - 3:
            # Near full – maybe consume some
            change = -random.randint(1, 3)
        else:
            # Normal range – random walk
            change = random.choice([-2, -1, 1, 2])
        
        new_stock = max(0, min(cap, stock + change))
        c.execute("UPDATE hotels SET lpg_stock = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (new_stock, hid))
    
    conn.commit()
    conn.close()
    st.sidebar.success(f"Updated {num_to_update} hotels with balanced changes!")
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📱 WhatsApp Reporting")
st.sidebar.info(
    "Hotel owners can report via WhatsApp Sandbox:\n\n"
    "1. Message +1 (415) 523-8886\n"
    "2. Send `join <sandbox-code>`\n"
    "3. Format: `HOTEL_ID surplus/shortage QTY`"
)

# 2. Dynamic Folium Map
st.subheader("📍 Live Cluster Inventory")
st.write("Real-time geographic distribution of LPG stock across Bengaluru hotels.")
m = create_hotel_map()
st_folium(m, width=1200, height=500)

st.divider()

# 3. Network Graph of Hotel Connections
st.subheader("🕸️ Real-time Matching Graph")
st.write(f"Visualizing optimal swap paths in {ward}. Nodes represent hotels; lines represent matched swap logistics.")

def create_matching_graph():
    G = nx.DiGraph()
    
    # Get recent swaps filtered by ward
    swaps_data = query_db(DB_PATH, """
        SELECT h1.name as from_n, h2.name as to_n, s.cylinders
        FROM swaps s
        JOIN hotels h1 ON s.from_hotel_id = h1.id
        JOIN hotels h2 ON s.to_hotel_id = h2.id
        WHERE h1.ward = ? OR h2.ward = ?
        ORDER BY s.timestamp DESC LIMIT 15
    """, (ward, ward))
    
    if swaps_data is None or swaps_data.empty:
        # Fallback to a few static nodes if no swaps yet
        G.add_node("Central Hub")
        G.add_node("Indiranagar Cluster")
    else:
        for _, row in swaps_data.iterrows():
            G.add_edge(row['from_n'], row['to_n'], weight=row['cylinders'])
    
    if len(G.nodes()) == 0: return go.Figure()

    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#3498db'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="bottom center",
        marker=dict(
            showscale=False,
            color='#2ecc71',
            size=20,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=f'Live Logistics Network: {ward}',
                    showlegend=False,
                    template="plotly_dark",
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    return fig

st.plotly_chart(create_matching_graph(), use_container_width=True)

st.divider()

# 3. Swap Optimization (Real Logic)
st.subheader("🔮 Predictive Optimization")
client = get_api_client()

# Populating Optimization Inputs from Real Data
if ward_hotels is not None and not ward_hotels.empty:
    real_requests = []
    real_surplus = []
    for _, row in ward_hotels.iterrows():
        if row['lpg_stock'] < DEMAND_THRESHOLD:
            real_requests.append({
                'hotel_id': row['name'], 
                'lat': row['lat'], 
                'lng': row['lng'], 
                'demand': TARGET_STOCK - row['lpg_stock'], 
                'urgency': 5 if row['lpg_stock'] == 0 else 3
            })
        elif row['lpg_stock'] > SURPLUS_THRESHOLD:
            real_surplus.append({
                'hotel_id': row['name'], 
                'lat': row['lat'], 
                'lng': row['lng'], 
                'surplus': row['lpg_stock'] - SURPLUS_THRESHOLD
            })
    
    st.session_state.swap_requests = real_requests
    st.session_state.surplus_offers = real_surplus

# Fallback to mock if ward is empty
if not st.session_state.get('swap_requests') and not st.session_state.get('surplus_offers'):
    st.session_state.swap_requests = [
        {'hotel_id': 'Empire Resto (Mock)', 'lat': 12.93, 'lng': 77.58, 'demand': 5, 'urgency': 5},
    ]
    st.session_state.surplus_offers = [
        {'hotel_id': 'Hotel Royal (Mock)', 'lat': 12.94, 'lng': 77.57, 'surplus': 10}
    ]

col_a, col_b = st.columns(2)
with col_a:
    st.write("**Current Shortages (Demand)**")
    st.table(pd.DataFrame(st.session_state.swap_requests))
with col_b:
    st.write("**Current Surplus (Offers)**")
    st.table(pd.DataFrame(st.session_state.surplus_offers))

if st.button("🔍 Find Optimal Swaps", type="primary"):
    with st.spinner("Optimizing fuel distribution..."):
        result = client.optimize_swaps(st.session_state.swap_requests, st.session_state.surplus_offers)
    
    if result.get('swaps'):
        st.success(f"✅ Found {len(result['swaps'])} optimal swaps")
        swaps_df = pd.DataFrame(result['swaps'])
        st.dataframe(swaps_df)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Cylinders Moved", result['total_cylinders_moved'])
        c2.metric("Distance Saved", f"{result['total_distance_saved']} km")
    else:
        st.warning("No optimal swaps found or matching backend not reachable.")

st.divider()

# 4. Swap Ticker
st.subheader("🔄 Recent Successful Swaps")
swaps_df = query_db(DB_PATH, """
    SELECT s.timestamp, h1.name as 'From', h2.name as 'To', s.cylinders as 'Quantity',
           '₹' || (s.cylinders * 100) as 'Savings'
    FROM swaps s
    JOIN hotels h1 ON s.from_hotel_id = h1.id
    JOIN hotels h2 ON s.to_hotel_id = h2.id
    ORDER BY s.timestamp DESC LIMIT 5
""")

if swaps_df is not None and not swaps_df.empty:
    st.table(swaps_df)
else:
    st.info("No recent swaps recorded. Waiting for Matcher Agent to run.")

st.info("💡 **Why this matters**: In a shortage, Layer 1 (AI) predicts the price hike. Layer 2 (Hive) immediately starts moving fuel from low-risk to high-risk zones before the price hits the street.")
