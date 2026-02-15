import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FeatureService:
    def __init__(self):
        pass

    def calculate_log_returns(self, df: pd.DataFrame) -> pd.Series:
        """Calculate logarithmic returns."""
        return np.log(df['close'] / df['close'].shift(1))

    def calculate_garman_klass_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate Garman-Klass volatility.
        GK = 0.5 * ln(High/Low)^2 - (2ln(2)-1) * ln(Close/Open)^2
        """
        log_hl = np.log(df['high'] / df['low'])
        log_co = np.log(df['close'] / df['open'])
        
        gk_var = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2
        return np.sqrt(gk_var.rolling(window=window).mean())

    def calculate_spread_factor(self, df: pd.DataFrame, spread_col: str = 'spread', window: int = 20) -> pd.Series:
        """Calculate spread widening factor relative to rolling mean."""
        rolling_mean = df[spread_col].rolling(window=window).mean()
        # Avoid division by zero
        return df[spread_col] / rolling_mean.replace(0, np.nan)

    def calculate_displacement_percentile(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate the percentile of the current absolute displacement relative to history.
        """
        displacement = (df['close'] - df['close'].shift(1)).abs()
        return displacement.rolling(window=window).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)

    def calculate_rolling_correlation(self, series1: pd.Series, series2: pd.Series, window: int = 50) -> pd.Series:
        """Calculate rolling correlation between two series."""
        return series1.rolling(window=window).corr(series2)

    def calculate_session_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculates standard deviation of log returns."""
        log_rets = self.calculate_log_returns(df)
        return log_rets.rolling(window=window).std()

    def process_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all features for the given DataFrame.
        Assumes columns: open, high, low, close, spread
        """
        df = df.copy()
        
        # Core checks
        required_cols = ['open', 'high', 'low', 'close', 'spread']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df['log_return'] = self.calculate_log_returns(df)
        df['gk_vol'] = self.calculate_garman_klass_volatility(df)
        df['spread_factor'] = self.calculate_spread_factor(df)
        df['displacement_pct'] = self.calculate_displacement_percentile(df)
        df['session_vol'] = self.calculate_session_volatility(df)
        
        # Fill NaNs or drop them logic could go here
        # For now, we keep them as is or fill with 0 carefully
        df.fillna(0, inplace=True) # Simple filling for initial implementation
        
        return df

feature_service = FeatureService()
