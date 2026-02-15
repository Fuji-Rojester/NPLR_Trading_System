import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

# Regime mapping matching the training classes (0, 1, 2)
# Ideally this should be configurable or part of the model metadata
REGIMES = ["Stable_Flow", "Directional_Vol", "Event_Risk"]

class RegimeService:
    def __init__(self, model_path: str = "backend/models/regime_model.joblib"):
        self.model = None
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        """Load the pre-trained model."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded regime model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning(f"Model not found at {self.model_path}")

    def calculate_entropy(self, probs: np.ndarray) -> float:
        """Calculate Shannon entropy of the probability distribution."""
        # Add epsilon to avoid log(0)
        probs = np.clip(probs, 1e-10, 1.0)
        return -np.sum(probs * np.log(probs))

    def predict_regime(self, features: pd.DataFrame) -> Optional[Dict]:
        """
        Predict regime probabilities and calculate entropy.
        Expected features columns should match model training.
        Returns a dict with probabilities, entropy, and tradeable flag.
        """
        if not self.model:
            logger.error("Model not loaded.")
            return None

        try:
            # Predict probabilities
            # Ensure features match model input. For now assuming correct order/columns.
            probs = self.model.predict_proba(features)[0]
            
            entropy = self.calculate_entropy(probs)
            
            # Map probabilities to regime names
            result = {
                "prob_stable": float(probs[0]) if len(probs) > 0 else 0.0,
                "prob_directional": float(probs[1]) if len(probs) > 1 else 0.0,
                "prob_event": float(probs[2]) if len(probs) > 2 else 0.0,
                "entropy": float(entropy),
                "timestamp": datetime.now().isoformat()
            }
            
            # Tradeable logic: P(Stable) > threshold AND Entropy < threshold
            # Thresholds should be in config, hardcoded for now as per docs
            STABLE_THRESHOLD = 0.5
            ENTROPY_THRESHOLD = 1.0 # High entropy blocks trading
            
            is_stable = result["prob_stable"] > STABLE_THRESHOLD
            low_entropy = result["entropy"] < ENTROPY_THRESHOLD
            
            result["tradeable"] = is_stable and low_entropy
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None

from datetime import datetime
