#!/usr/bin/env python3
"""
Predictor agent - retrains models and updates predictions
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
import joblib
from tensorflow.keras.models import load_model

# Add base directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.api.models.database import update_predictions
from backend.core.layer1_geopolitical.models.train_pipeline import MEGHTrainer

def run_predictor():
    print(f"[{datetime.now()}] Predictor agent started")
    
    models_dir = os.path.join(BASE_DIR, "backend", "core", "layer1_geopolitical", "models", "saved")
    lstm_path = os.path.join(models_dir, "lstm_shortage.keras")
    xgb_path = os.path.join(models_dir, "xgboost_shortage.pkl")
    scaler_path = os.path.join(models_dir, "lstm_scaler.pkl")

    # 1. Check if models exist, if not, train once
    if not all([os.path.exists(p) for p in [lstm_path, xgb_path, scaler_path]]):
        print("Models missing. Starting initial training...")
        trainer = MEGHTrainer()
        trainer.train()
    else:
        print("Models found. Loading for inference.")
        # Optional: periodically retrain
        trainer = MEGHTrainer() 
    
    # 2. Load models
    lstm_model = load_model(lstm_path)
    xgb_model = joblib.load(xgb_path)
    scaler = joblib.load(scaler_path)
    
    # 3. Generate predictions for all wards
    # For MVP, we'll iterate through our key wards
    wards = ["Malleswaram", "Jayanagar", "Indiranagar", "Whitefield"]
    
    # In a real app, this would use live data per ward.
    # For the demo, we'll use the latest global predictions with some ward-specific variance
    
    # Get latest features
    df = trainer.load_data()
    feature_cols = ['price', 'event_intensity', 'price_lag_1', 'price_lag_3', 'price_lag_7', 'price_ma7', 'price_std7']
    latest_data = df[feature_cols].iloc[-14:].values # Last 14 days for LSTM
    
    # Reshape and scale for LSTM
    latest_scaled = scaler.transform(latest_data).reshape(1, 14, len(feature_cols))
    
    # LSTM probability
    lstm_prob = float(lstm_model.predict(latest_scaled)[0][0])
    
    # XGBoost probability
    xgb_prob = float(xgb_model.predict_proba(df[feature_cols].iloc[-1:].values)[0][1])
    
    # Ensemble
    base_prob = (lstm_prob + xgb_prob) / 2
    
    predictions = []
    for ward in wards:
        # Add some ward-specific noise for visual variety in heatmap
        variance = (hash(ward) % 10) / 100.0
        prob = min(0.99, max(0.01, base_prob + variance - 0.05))
        
        predictions.append({
            'ward': ward,
            'probability': round(prob, 2),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # 4. Store in database
    update_predictions(predictions)
    print(f"Updated predictions for {len(predictions)} wards.")

if __name__ == "__main__":
    run_predictor()
