#!/usr/bin/env python3
"""
MEGH Live Demo Orchestrator
Runs all background agents in parallel threads for a seamless demonstration.
"""

import threading
import time
import sys
import os
import signal
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from agents.data_collector.run import run_data_collector
from agents.expert_monitor.run import run_expert_monitor
from agents.ship_tracker.run import run_ship_tracker
from agents.predictor.run import run_predictor
from agents.matcher.run import run_matcher

def agent_wrapper(name, target, interval_seconds):
    """Wrapper to run an agent function periodically"""
    print(f"🚀 [Orchestrator] Starting {name} agent...")
    while True:
        try:
            print(f"[{datetime.now()}] {name}: Cycle started")
            target()
            print(f"[{datetime.now()}] {name}: Cycle completed. Sleeping for {interval_seconds}s.")
        except Exception as e:
            print(f"❌ [Orchestrator] Error in {name} agent: {e}")
        
        time.sleep(interval_seconds)

def main():
    print("====================================================")
    print("🔥 MEGH LIVE DEMO MODE ACTIVATED 🔥")
    print("Running all autonomous agents in parallel threads.")
    print("Press Ctrl+C to stop all agents.")
    print("====================================================")
    
    agents = [
        {"name": "Data Collector", "target": run_data_collector, "interval": 600}, # 10 min
        {"name": "Expert Monitor", "target": run_expert_monitor, "interval": 1800}, # 30 min
        {"name": "Ship Tracker", "target": run_ship_tracker, "interval": 300},  # 5 min
        {"name": "Predictor", "target": run_predictor, "interval": 3600}, # 1 hour
        {"name": "Matcher", "target": run_matcher, "interval": 60}, # every minute for demo
    ]
    
    threads = []
    for agent in agents:
        t = threading.Thread(
            target=agent_wrapper, 
            args=(agent["name"], agent["target"], agent["interval"]),
            daemon=True
        )
        t.start()
        threads.append(t)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 [Orchestrator] Stopping all agents... Demo finished.")

if __name__ == "__main__":
    main()
