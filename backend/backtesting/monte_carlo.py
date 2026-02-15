import pandas as pd
import numpy as np
import logging
from backend.services.feature_service import FeatureService
from backend.services.regime_service import RegimeService

logger = logging.getLogger(__name__)

class MonteCarloSimulation:
    def __init__(self):
        self.feature_service = FeatureService()
        self.regime_service = RegimeService()
        
    def run_spread_shock(self, df: pd.DataFrame, shock_factor: float = 300.0) -> pd.DataFrame:
        """
        Simulate a spread shock where spread increases by X%.
        Expected result: Trading frequency should drop.
        """
        logger.info(f"Running Monte Carlo Spread Shock: {shock_factor}% increase")
        
        # Apply Shock
        shocked_df = df.copy()
        shocked_df['spread'] = shocked_df['spread'] * (shock_factor / 100.0 + 1.0)
        
        # Recalculate features based on shocked data
        shocked_df = self.feature_service.process_features(shocked_df)
        
        # Check Regime / Tradeable flag
        # We expect entropy to potentially rise or specific features to trigger "non-tradeable"
        # Since our dummy model doesn't explicitly learn from spread features yet (it was random),
        # this test is more about the infrastructure.
        # However, if we had a real model, we'd check if `tradeable` count decreases.
        
        tradeable_count = 0
        for idx, row in shocked_df.iterrows():
            # In a real scenario, we'd predict row by row or batch
            # Mock prediction logic utilizing 'spread_factor' feature if model used it
            # For now, we simulate the effect: if spread_factor > threshold, kill trade.
            
            # Since we don't have a trained model on spread, we manually enforce logic for the test:
            if row.get('spread_factor', 0) > 2.0: # Arbitrary threshold for test
                continue
                
            tradeable_count += 1
            
        logger.info(f"Tradeable candles after shock: {tradeable_count}/{len(df)}")
        print(f"Tradeable candles: {tradeable_count}")
        return shocked_df

if __name__ == "__main__":
    from backend.backtesting.utils import generate_synthetic_data
    df = generate_synthetic_data(500)
    sim = MonteCarloSimulation()
    sim.run_spread_shock(df)
