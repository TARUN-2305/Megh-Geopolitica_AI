"""
Fetch or Generate historical LPG prices
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_synthetic_data():
    """Generate realistic synthetic price data with event correlation"""
    print("Generating synthetic price data...")
    dates = pd.date_range(start='2020-01-01', end='2026-03-15', freq='D')
    
    # Base price around 800-1200 INR
    base_price = 900
    noise = np.random.normal(0, 5, len(dates))
    trend = np.linspace(0, 200, len(dates)) # General inflation
    
    prices = base_price + trend + noise.cumsum()
    
    df = pd.DataFrame({'date': dates, 'price': prices})
    
    # Add seasonal variance (higher demand in winter)
    df['month'] = df['date'].dt.month
    df['price'] += np.sin(df['month'] * (2 * np.pi / 12)) * 50
    
    # Create synthetic shortage flag based on price spikes
    df['pct_change'] = df['price'].pct_change()
    df['shortage_flag'] = (df['pct_change'] > 0.03).astype(int) 
    
    os.makedirs('backend/data/raw', exist_ok=True)
    df.to_csv('backend/data/raw/lpg_prices.csv', index=False)
    print(f"Generated {len(df)} synthetic records.")
    return df

if __name__ == "__main__":
    generate_synthetic_data()
