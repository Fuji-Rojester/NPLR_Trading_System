import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing.
    """
    dates = [datetime.now() - timedelta(minutes=n_samples - i) for i in range(n_samples)]
    
    # Random walk for price
    price = 100.0
    prices = []
    for _ in range(n_samples):
        change = np.random.normal(0, 0.1)
        price += change
        prices.append(price)
        
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p + abs(np.random.normal(0, 0.05)) for p in prices],
        'low': [p - abs(np.random.normal(0, 0.05)) for p in prices],
        'close': [p + np.random.normal(0, 0.02) for p in prices],
        'volume': np.random.randint(100, 1000, n_samples),
        'spread': np.abs(np.random.normal(0.01, 0.005, n_samples))
    })
    
    return df
