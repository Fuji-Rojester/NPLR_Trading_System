import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional
from collections import deque

logger = logging.getLogger(__name__)

class DriftMonitor:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)
        self.entropies = deque(maxlen=window_size)
        self.baseline_dist = None # Should be loaded from training artifact
        
    def update(self, predicted_return: float, actual_return: float, entropy: float):
        """
        Update monitor with latest trade outcome.
        """
        self.predictions.append(predicted_return)
        self.actuals.append(actual_return)
        self.entropies.append(entropy)
        
    def calculate_ic(self) -> float:
        """
        Calculate Information Coefficient (Correlation between pred and actual).
        """
        if len(self.predictions) < 30: # Minimum samples
            return 0.0
            
        return np.corrcoef(self.predictions, self.actuals)[0, 1]
        
    def calculate_entropy_avg(self) -> float:
        """
        Calculate rolling average entropy.
        """
        if not self.entropies:
            return 0.0
        return np.mean(self.entropies)
        
    def check_alerts(self) -> List[str]:
        """
        Check for drift triggers.
        """
        alerts = []
        ic = self.calculate_ic()
        entropy_avg = self.calculate_entropy_avg()
        
        # Thresholds from architecture
        if len(self.predictions) > 100 and ic < 0.02:
            alerts.append(f"Low IC ({ic:.4f}): Reduce Allocation")
            
        if len(self.predictions) > 100 and ic < 0.0:
            alerts.append(f"Negative IC ({ic:.4f}): Decommission Model")
            
        if entropy_avg > 1.5: # Arbitrary high entropy threshold
            alerts.append(f"High Entropy ({entropy_avg:.4f}): Suspend Trading")
            
        return alerts

    def calculate_kl_divergence(self, current_dist: np.ndarray, baseline_dist: np.ndarray) -> float:
        """
        Calculate KL Divergence: sum(P * log(P / Q))
        """
        # Add epsilon
        epsilon = 1e-10
        current_dist = np.clip(current_dist, epsilon, 1.0)
        baseline_dist = np.clip(baseline_dist, epsilon, 1.0)
        
        # Normalize
        current_dist /= current_dist.sum()
        baseline_dist /= baseline_dist.sum()
        
        return np.sum(current_dist * np.log(current_dist / baseline_dist))
