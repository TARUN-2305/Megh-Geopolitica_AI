# MEGH (ಮೇಘ) - "Cloud" in Kannada
### Geopolitical AI + Human Expert Intelligence + Hyper-local Resilience

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![BuildWithAI](https://img.shields.io/badge/Hackathon-BuildWithAI-orange.svg)

---

## 🚀 Project Overview
**MEGH (ಮೇಘ)** is an autonomous, multi-layered AI platform designed to turn geopolitical chaos into community resilience. During the global LPG supply chain disruption of March 2026, many restaurants in Karnataka (like the iconic Kadamba and Adyar Ananda Bhavan) were forced to shut down or reduce menus. MEGH addresses this by predicting supply shocks and orchestrating hyper-local resource sharing.

## 🏗️ Architecture
The system consists of four layers of intelligence and a global monitoring eye:

- **Layer 0 (Wisdom)**: Human Expert Intelligence extraction from geopolitical analysts via YouTube transcripts and Gemini 2.5 Flash.
- **Layer 1 (Geopolitical Eye)**: Hybrid AI prediction (LSTM + XGBoost + Bayesian Networks) forecasting city-wide supply shocks.
- **Layer 2 (The Hive)**: P2P Fuel Swap Market using PuLP Linear Programming for optimal resource redistribution.
- **Layer 3 (The Heart)**: Worker displacement protection via TF-IDF skill-based matchmaking.
- **Global Eye**: Real-time AIS ship tracking at critical maritime chokepoints.

### 🖼️ Visualizing Resilience

#### Layer 1: Geopolitical Eye (Explaining the Shock)
![Chain of Thought](docs/images/wisdom.png)
*The 'Chain of Thought' page uses Bayesian Causal Inference to explain **why** a shortage is occurring. It traces global events (like the Strait of Hormuz naval drills) to local price impacts, providing a transparent reasoning path.*

#### Layer 2: The Hive (Orchestrating the Action)
![P2P Swap Market](docs/images/hive.png)
*The Logistics Network Graph dynamically maps fuel swap requests. Nodes represent hotels, and edges represent optimized delivery paths calculated to minimize urban congestion and travel distance.*

#### Layer 3: The Heart (Protecting the People)
![Worker Protection](docs/images/heart.png)
*The Worker Protection dashboard manages the social impact. It provides real-time statistics on protected workers, average daily wages saved, and direct skill-match history for hospitality gig workers.*

#### Global Eye (Watching the World)
![Ship Tracking](docs/images/global_eye.png)
*Our Maritime Monitor tracks AIS signals at global chokepoints. Tanker diversions or idling at the Port of Fujairah act as early leading indicators for MEGH's predictive models.*

## 🛠️ Tech Stack
- **AI/ML**: TensorFlow, XGBoost, Scikit-learn, pgmpy (Bayesian Inference)
- **NLP**: Google Gemini 2.5 Flash, TF-IDF
- **Optimization**: PuLP (Coin-OR)
- **Backend**: FastAPI, SQLite3
- **Frontend**: Streamlit, Plotly, Folium (Maps), NetworkX
- **Messaging**: Twilio WhatsApp API

## 📦 Setup & Installation
1. **Clone the Repo**:
   ```bash
   git clone https://github.com/TARUN-2305/Megh-Geopolitica_AI.git
   cd Megh-Geopolitica_AI
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY` and `NEWSAPI_KEY`.
4. **Run the Engines**:
   - **Backend API**: `python -m uvicorn backend.api.main:app --reload`
   - **Autonomous Agents**: `python scripts/live_demo.py`
   - **Visual Dashboard**: `streamlit run frontend/app.py`

## 📱 WhatsApp Demo
You can simulate live stock updates using the Twilio WhatsApp Sandbox:
- Join the sandbox by messaging `join <sandbox-code>` to +1 (415) 523-8886.
- Format: `HOTEL_ID surplus/shortage QTY` (e.g., `12 surplus 5`).

## 🔍 Deep Dive
For a full technical breakdown of the models, data flow, and optimization logic, see [docs/deep_dive.md](docs/deep_dive.md).

## 📜 License
Independent project licensed under the MIT License. See [LICENSE](LICENSE) for details.

---
**MEGH: Turning Geopolitical Chaos into Regional Stability.**
