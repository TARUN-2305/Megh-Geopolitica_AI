import streamlit as st
import plotly.graph_objects as go
import networkx as nx

import json
import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.core.layer0_wisdom.insight_extractor import get_gemini_model
from backend.core.layer1_geopolitical.models.causal_graph import build_causal_graph
from pgmpy.inference import VariableElimination

def generate_explanation(scenario, custom_text=None):
    """Generate explanation using hardcoded scenarios or Gemini for custom input"""
    if scenario == "Custom input" and custom_text:
        try:
            model = get_gemini_model()
            prompt = f"""
            You are MEGH (Master Execution & Governance Handler), an AI predicting geopolitical impacts on Bengaluru.
            Given the following event: "{custom_text}"
            
            Generate a JSON response that traces the causal path from this event to local LPG prices in Bengaluru.
            JSON structure:
            {{
                "event": "Short descriptive title",
                "source": "Realistic source name",
                "event_confidence": "High/Medium/Low",
                "propagation": ["Step 1", "Step 2", "Step 3", "Step 4"],
                "market_impact": {{
                    "brent": percentage_change_float,
                    "brent_delta": daily_delta_float,
                    "freight": percentage_change_float,
                    "freight_delta": daily_delta_float,
                    "usd_inr": "current_rate_string",
                    "usd_inr_delta": "daily_delta_string"
                }},
                "local_price": current_lpg_price_int,
                "price_delta": percentage_change_int,
                "narrative": "A 2-sentence explanation of the cascade.",
                "action": "One specific resilient action for local hotels."
            }}
            Return ONLY the raw JSON.
            """
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            st.error(f"Gemini error: {e}")
            return None

    # Hardcoded scenarios for demo reliability
    if "Houthi" in scenario:
        return {
            'event': "Red Sea Drone Attacks",
            'source': "Maritime Bulletin / Prashant Dhawan",
            'event_confidence': "High",
            'propagation': [
                "Vessels diverted around Cape of Good Hope",
                "Shipping time increased by 10-14 days",
                "Fuel surcharge applied by MSC and Maersk",
                "Indian ports report delayed crude arrivals"
            ],
            'market_impact': {
                'brent': 4.2, 'brent_delta': 1.2,
                'freight': 15.0, 'freight_delta': 5.0,
                'usd_inr': "83.1", 'usd_inr_delta': "0.05"
            },
            'local_price': 1105, 'price_delta': 12,
            'narrative': "The blockade in the Red Sea is cascading through the freight market, increasing 'landed cost' of LPG in Mangaluru port.",
            'action': "Advise collective buying for Jayanagar hotel cluster to hedge against next week's hike."
        }
    elif "Russia" in scenario:
        return {
            'event': "Black Sea Infrastructure Strike",
            'source': "Abhijit Chavda / Reuters",
            'event_confidence': "Medium",
            'propagation': [
                "Global natural gas futures spike on supply fears",
                "European demand redirected to Middle East supply",
                "Spot prices for LPG in Asia rise due to bidding wars"
            ],
            'market_impact': {
                'brent': 2.1, 'brent_delta': 0.8,
                'freight': 2.0, 'freight_delta': 0.5,
                'usd_inr': "82.9", 'usd_inr_delta': "-0.1"
            },
            'local_price': 1080, 'price_delta': 5,
            'narrative': "European supply shocks are pulling cargo away from India, forcing local distributors to tap high-priced spot markets.",
            'action': "Alert Malleswaram hotels to check existing inventory; suggest 3-day hold on non-essential swaps."
        }
    elif "Hormuz" in scenario:
        return {
            'event': "Strait of Hormuz Naval Drills",
            'source': "Chanakyan / IRGC Press",
            'event_confidence': "High",
            'propagation': [
                "Insurance premiums for tankers jump 300%",
                "Tanker queues at Fujairah increase",
                "Local inventory in India falls to 4-day reserve"
            ],
            'market_impact': {
                'brent': 7.5, 'brent_delta': 3.5,
                'freight': 25.0, 'freight_delta': 12.0,
                'usd_inr': "83.5", 'usd_inr_delta': "0.4"
            },
            'local_price': 1250, 'price_delta': 25,
            'narrative': "Hormuz tension is the 'Kill Switch' for Indian LPG. 60% of our supply passes through here. Probability of total shortage in 72 hours is 🔴 CRITICAL.",
            'action': "IMMEDIATE: Trigger P2P Hive swaps. Move surplus from Industrial zones to Residential hubs."
        }
    return None

st.set_page_config(layout="wide", page_title="MEGH Chain of Thought")
st.title("🔍 Chain of Thought: Why MEGH Predicts What It Predicts")

if 'current_explanation' not in st.session_state:
    st.session_state.current_explanation = None

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Select a Scenario")
    scenario = st.selectbox(
        "Choose a geopolitical event:",
        ["Houthi blockade threat (March 2026)", "Russia-Ukraine escalation", "Strait of Hormuz tension", "Custom input"]
    )
    if scenario == "Custom input":
        custom_event = st.text_area("Describe the event:", height=100)

with col2:
    st.subheader("2. View Expert Consensus")
    experts = {
        "Prashant Dhawan": {"agreement": 0.85, "quote": "Red Sea disruptions will impact oil within 2 weeks"},
        "Abhijit Chavda": {"agreement": 0.92, "quote": "The strait closure risk is real and imminent"},
        "Chanakyan": {"agreement": 0.78, "quote": "Middle East tension = Kerala fuel price hike"}
    }
    for expert, data in experts.items():
        with st.expander(f"{expert} - {data['agreement']*100:.0f}% confidence"):
            st.write(f"📌 {data['quote']}")
            st.progress(data['agreement'])

if st.button("🔮 Generate Chain of Thought", type="primary"):
    with st.spinner("Tracing the butterfly effect..."):
        c_text = custom_event if scenario == "Custom input" else None
        st.session_state.current_explanation = generate_explanation(scenario, c_text)

if st.session_state.current_explanation:
    st.divider()
    st.subheader("3. The Causal Path")
    col_a, col_b, col_c, col_d = st.columns(4)
    exp = st.session_state.current_explanation
    with col_a:
        st.markdown("### 🌍 Event")
        st.info(exp['event'])
        st.caption(f"Source: {exp['source']}")
        st.caption(f"Confidence: {exp['event_confidence']}")
    with col_b:
        st.markdown("### 🔄 Propagation")
        for step in exp['propagation']:
            st.write(f"→ {step}")
    with col_c:
        st.markdown("### 📈 Market Impact")
        met = exp['market_impact']
        st.metric("Brent Crude", f"{met['brent']}%", delta=f"{met['brent_delta']}%")
        st.metric("Freight Cost", f"{met['freight']}%", delta=f"{met['freight_delta']}%")
    with col_d:
        st.markdown("### 🏘️ Local Impact")
        st.metric("Bengaluru LPG Price", f"₹{exp['local_price']}", delta=f"{exp['price_delta']}%")
        risk_data = {"Malleswaram": "🔴 High", "Jayanagar": "🟡 Medium", "Indiranagar": "🟢 Low"}
        for area, risk in risk_data.items():
            st.write(f"{area}: {risk}")
    
    st.divider()
    st.subheader("4. Bayesian Causal Graph")
    st.write("Calculated via MEGH's internal probabilistic PGMPY model.")
    
    # Build and infer
    model = build_causal_graph()
    infer = VariableElimination(model)
    
    # Map scenario to evidence
    evidence = {}
    if "Houthi" in scenario: evidence = {"Strait_Blockage": 2} # Full blockage
    elif "Russia" in scenario: evidence = {"Conflict_Intensity": 2} # High conflict
    elif "Hormuz" in scenario: evidence = {"Strait_Blockage": 2, "Conflict_Intensity": 2}
    
    # Calculate shortage probability
    q = infer.query(variables=['Shortage_Probability'], evidence=evidence)
    shortage_prob = q.values[2] # Prob of 'High' shortage
    
    st.metric("Model-Calculated Shortage Probability", f"{shortage_prob*100:.1f}%")

    G = nx.DiGraph()
    G.add_edges_from(model.edges())
    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#555'), hoverinfo='none', mode='lines')
    
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=list(G.nodes()),
        textposition="top center",
        marker=dict(size=20, color='#3498db', line_width=2))
        
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    template="plotly_dark",
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    st.plotly_chart(fig, use_container_width=True)
