import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score

# Import local modules
from src.feature_engine import NPLRFeatureEngineer
from src.labeling import BarrierLabeler

def run_training_pipeline(data_path):
    print("1. Loading Data...")
    # Mock data loading - Replace with pd.read_csv(data_path)
    # Using the dummy generator from previous step for structure
    dates = pd.date_range(start="2024-01-01", periods=5000, freq="1min")
    df = pd.DataFrame({
        'Open': np.random.normal(1.1000, 0.0005, 5000).cumsum(),
        'Volume': np.random.randint(100, 1000, 5000)
    }, index=dates)
    df['High'] = df['Open'] + 0.0002
    df['Low'] = df['Open'] - 0.0002
    df['Close'] = df['Open'] + np.random.normal(0, 0.0001, 5000)

    print("2. Engineering Features...")
    engineer = NPLRFeatureEngineer(lookback_window=60)
    features = engineer.process(df)
    
    print("3. Creating Labels (The 'Truth')...")
    labeler = BarrierLabeler(profit_thresh=0.0003, stop_thresh=0.0003)
    target = labeler.apply(df['Close'])
    
    # Align indices (Features drop NaNs, Labels need to match)
    aligned_data = features.join(target.rename('target'), how='inner')
    
    X = aligned_data.drop('target', axis=1)
    y = aligned_data['target']

    print("4. Splitting Data (Time-Series Split)...")
    # STRICTLY sequential split. No random shuffling here.
    train_size = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    print("5. Training Random Forest...")
    # Limiting depth to prevent overfitting
    model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=20, random_state=42)
    model.fit(X_train, y_train)

    print("6. Initial Validation...")
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
    
    # Key Metric: Precision on Class 1 (Safe)
    # We care more about "When we say it's safe, is it actually safe?" 
    # than catching every opportunity.
    precision = precision_score(y_test, preds)
    print(f"Precision (Win Rate of Regime Call): {precision:.2%}")
    
    return model, X_test, y_test