import pandas as pd
import numpy as np
import logging
from backend.backtesting.utils import generate_synthetic_data
from backend.services.feature_service import FeatureService
from backend.services.regime_service import RegimeService

logger = logging.getLogger(__name__)

class WalkForwardBacktester:
    def __init__(self):
        self.feature_service = FeatureService()
        self.regime_service = RegimeService()
        
    def run_backtest(self, df: pd.DataFrame, window_size: int = 100, step_size: int = 10):
        """
        Run a simple walk-forward backtest.
        Train on [t-window, t], Test on [t, t+step]
        For this simplified version, we just simulate the 'test' phase 
        by checking if the regime allowed trading and calculating returns.
        """
        logger.info("Starting Walk-Forward Backtest...")
        
        # 1. Compute Features
        df = self.feature_service.process_features(df)
        
        results = []
        equity = 10000.0
        
        # Iterate through data
        for i in range(window_size, len(df), step_size):
            train_data = df.iloc[i-window_size:i]
            test_data = df.iloc[i:min(i+step_size, len(df))]
            
            # In a real WF, we'd retrain the model here using train_data
            # self.regime_service.train(train_data) 
            
            for idx, row in test_data.iterrows():
                # Predict Regime
                # We need to reshape or prepare row as DataFrame
                row_df = pd.DataFrame([row])
                # Mocking features expected by model (5 cols) for now if needed, 
                # but our service expects full feature df. 
                # Ideally we pass the feature vector.
                # For this implementation, we'll assume the model handles the features present.
                
                # IMPORTANT: The dummy model was trained on 5 dummy features. 
                # Real model needs 5 specific features.
                # We'll use the 'close' price to generate dummy return for PnL
                
                # Check Logic
                # 1. Regime says tradeable?
                # 2. If yes, generate signal (Edge Engine - not implemented yet)
                # 3. Calculate PnL
                
                # Mocking Signal
                signal = 1 if np.random.random() > 0.5 else -1
                
                # PnL = Signal * Return
                log_ret = row.get('log_return', 0)
                pnl = equity * signal * log_ret
                equity += pnl
                
                results.append({
                    'timestamp': row['timestamp'],
                    'equity': equity,
                    'pnl': pnl
                })
                
        results_df = pd.DataFrame(results)
        logger.info(f"Backtest complete. Final Equity: {equity}")
        print(f"Final Equity: {equity}")
        return results_df

if __name__ == "__main__":
    df = generate_synthetic_data(500)
    backtester = WalkForwardBacktester()
    backtester.run_backtest(df)
