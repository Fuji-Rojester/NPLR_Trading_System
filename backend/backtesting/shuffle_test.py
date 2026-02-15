import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ShuffleTest:
    def run_test(self, returns: pd.Series):
        """
        Shuffle the returns and calculate performance metrics.
        Expected: Sharpe Ratio should approach zero.
        """
        logger.info("Running Shuffle Test...")
        
        shuffled_returns = returns.sample(frac=1).reset_index(drop=True)
        
        # Calculate Sharpe
        mean_ret = shuffled_returns.mean()
        std_ret = shuffled_returns.std()
        sharpe = mean_ret / std_ret * np.sqrt(252*1440) # Ann. assuming minute data
        
        logger.info(f"Shuffled Sharpe: {sharpe}")
        print(f"Shuffled Sharpe: {sharpe}")
        
        # Validate
        if abs(sharpe) > 1.0:
            logger.warning("High Sharpe on shuffled data! Possible look-ahead bias or anomaly.")
        else:
            logger.info("Shuffle test passed (Sharpe collapsed).")

if __name__ == "__main__":
    from backend.backtesting.utils import generate_synthetic_data
    from backend.services.feature_service import FeatureService
    
    df = generate_synthetic_data(500)
    fs = FeatureService()
    df = fs.process_features(df)
    
    tester = ShuffleTest()
    tester.run_test(df['log_return'].dropna())
