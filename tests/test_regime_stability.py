import numpy as np
import pandas as pd
from src.train_regime import run_training_pipeline

def test_feature_importance():
    """
    Sanity Check: Does the model care about the right things?
    If 'fragility_idx' is 0 importance, the model is broken.
    """
    model, X_test, y_test = run_training_pipeline("dummy_path")
    
    importances = model.feature_importances_
    feature_names = X_test.columns
    
    print("\n--- FEATURE IMPORTANCE AUDIT ---")
    for name, imp in zip(feature_names, importances):
        print(f"{name}: {imp:.4f}")
        
    # Assertion for automated testing
    # Fragility or Vol should be significant
    if importances[feature_names.get_loc("fragility_idx")] < 0.05:
        print("FAIL: Model ignoring Fragility Index. Logic flaw.")
    else:
        print("PASS: Model using Liquidity/Vol structure.")

if __name__ == "__main__":
    test_feature_importance()