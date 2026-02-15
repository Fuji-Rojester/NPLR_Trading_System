import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import joblib
import os

MODEL_PATH = "backend/models/regime_model.joblib"

def train_dummy_model():
    print("Training dummy regime model...")
    # Generate synthetic data: 1000 samples, 5 features, 3 classes (Stable, Directional, Event)
    X, y = make_classification(n_samples=1000, n_features=5, n_informative=3, n_classes=3, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_dummy_model()
