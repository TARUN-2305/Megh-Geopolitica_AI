"""
Complete training pipeline for LSTM + XGBoost ensemble
Uses historical event data and price data to forecast LPG shortages
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os

# ML libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb

# TensorFlow/Keras for LSTM
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Define paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
EVENTS_DB = os.path.join(BASE_DIR, "backend", "data", "raw", "events.db")
PRICES_CSV = os.path.join(BASE_DIR, "backend", "data", "raw", "lpg_prices.csv")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "core", "layer1_geopolitical", "models", "saved")

class MEGHTrainer:
    def __init__(self, db_path=EVENTS_DB, price_data_path=PRICES_CSV):
        self.db_path = db_path
        self.price_data_path = price_data_path
        self.models_dir = MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        
    def load_data(self):
        """Load and merge event data with price data"""
        print(f"Loading prices from {self.price_data_path}...")
        prices_df = pd.read_csv(self.price_data_path)
        prices_df['date'] = pd.to_datetime(prices_df['date'])
        
        # Load events from DB if exists
        events_df = pd.DataFrame(columns=['date', 'event_intensity'])
        if os.path.exists(self.db_path):
            print(f"Loading events from {self.db_path}...")
            conn = sqlite3.connect(self.db_path)
            raw_events = pd.read_sql_query("SELECT date, title FROM events", conn)
            conn.close()
            
            # Map intensity
            intensity_map = {'blockade': 0.9, 'sanction': 0.7, 'conflict': 0.8, 'attack': 0.85, 'tension': 0.6}
            def get_intensity(title):
                title = str(title).lower()
                for k, v in intensity_map.items():
                    if k in title: return v
                return 0.2
            
            raw_events['event_intensity'] = raw_events['title'].apply(get_intensity)
            raw_events['date'] = pd.to_datetime(raw_events['date']).dt.tz_localize(None).dt.normalize()
            events_df = raw_events.groupby('date')['event_intensity'].max().reset_index()
        else:
            print("No events database found. Using empty events.")
        
        # Merge
        df = pd.merge(prices_df, events_df, on='date', how='left').fillna(0)
        
        # Features
        for lag in [1, 3, 7]:
            df[f'price_lag_{lag}'] = df['price'].shift(lag)
        
        df['price_ma7'] = df['price'].rolling(7).mean()
        df['price_std7'] = df['price'].rolling(7).std()
        
        return df.dropna().reset_index(drop=True)
    
    def prepare_sequences(self, df, seq_len=14):
        feature_cols = ['price', 'event_intensity', 'price_lag_1', 'price_lag_3', 'price_lag_7', 'price_ma7', 'price_std7']
        data = df[feature_cols].values
        targets = df['shortage_flag'].values
        
        X, y = [], []
        for i in range(len(data) - seq_len):
            X.append(data[i:i+seq_len])
            y.append(targets[i+seq_len])
        return np.array(X), np.array(y)
    
    def train(self):
        df = self.load_data()
        X_seq, y_seq = self.prepare_sequences(df)
        
        split = int(0.8 * len(X_seq))
        X_train, X_test = X_seq[:split], X_seq[split:]
        y_train, y_test = y_seq[:split], y_seq[split:]
        
        # Scale
        scaler = StandardScaler()
        X_train_reshaped = X_train.reshape(-1, X_train.shape[-1])
        scaler.fit(X_train_reshaped)
        joblib.dump(scaler, os.path.join(self.models_dir, "lstm_scaler.pkl"))
        
        X_train_scaled = scaler.transform(X_train_reshaped).reshape(X_train.shape)
        X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
        
        # LSTM
        print("Training LSTM...")
        model = Sequential([
            LSTM(32, input_shape=(X_train.shape[1], X_train.shape[2])),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X_train_scaled, y_train, validation_data=(X_test_scaled, y_test), epochs=10, batch_size=16, verbose=0)
        model.save(os.path.join(self.models_dir, "lstm_shortage.keras"))
        
        # XGBoost
        print("Training XGBoost...")
        X_tab = df[['price', 'event_intensity', 'price_lag_1', 'price_lag_3', 'price_lag_7', 'price_ma7', 'price_std7']].values
        y_tab = df['shortage_flag'].values
        
        xgb_model = xgb.XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1)
        xgb_model.fit(X_tab[:split], y_tab[:split])
        joblib.dump(xgb_model, os.path.join(self.models_dir, "xgboost_shortage.pkl"))
        
        print("Model training complete.")
        return True

if __name__ == "__main__":
    MEGHTrainer().train()
