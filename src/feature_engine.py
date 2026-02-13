import pandas as pd
import numpy as np
from typing import Tuple, Optional

class NPLRFeatureEngineer:
    """
    Non-Parametric Liquidity Reversion (NPLR) Feature Engineering.
    
    Transforms raw OHLCV data into statistical state vectors representing:
    1. Volatility Regime (Normalized by Diurnal Cycle)
    2. Liquidity Stress (Inverse Amihud)
    3. Structural Displacement (Percentile Rank)
    """

    def __init__(self, 
                 lookback_window: int = 60, 
                 tod_window: int = 20):
        """
        :param lookback_window: Window size for displacement ranking (e.g., 60 mins).
        :param tod_window: Rolling window (in days) to calculate Time-of-Day baselines.
        """
        self.lookback = lookback_window
        self.tod_window = tod_window
        # Constant for Parkinson Volatility scaling (sqrt(1 / (4 * ln(2))))
        self.parkinson_const = 1.0 / np.sqrt(4 * np.log(2))

    def _calculate_parkinson_vol(self, high: pd.Series, low: pd.Series) -> pd.Series:
        """
        Estimates volatility using High-Low range. 
        More robust to opening jumps and drift than Close-Close std dev.
        """
        # Logarithmic High-Low range
        log_hl = np.log(high / low)
        # Squared range
        rs = log_hl ** 2
        return np.sqrt(rs) * self.parkinson_const

    def _normalize_seasonality(self, df: pd.DataFrame, target_col: str) -> pd.Series:
        """
        Normalizes a metric by its Time-of-Day (ToD) expectation.
        Formula: Raw_Metric / Median_Metric_at_this_Time
        """
        # Create a minute-of-day key for grouping
        # Note: In production, handle TimeZones carefully (e.g., UTC).
        temp_df = df.copy()
        temp_df['minute_idx'] = temp_df.index.hour * 60 + temp_df.index.minute
        
        # Calculate rolling baseline per minute-of-day
        # We group by minute_idx, then take the rolling mean of the last 'tod_window' days
        # Since this is complex to vectorize efficiently in pandas without lookahead bias,
        # we simplify for this blueprint: Global Median per minute_idx (Expanding window)
        
        # Expanding median to prevent lookahead bias
        baseline = temp_df.groupby('minute_idx')[target_col].expanding().median().reset_index(level=0, drop=True)
        
        # Realign baseline with original index
        aligned_baseline = baseline.sort_index()
        
        # Calculate Relative Ratio (Clip to avoid infinity)
        rel_metric = temp_df[target_col] / aligned_baseline.replace(0, np.nan)
        return rel_metric.fillna(1.0) # Default to 1.0 (normal) if no history

    def _calculate_liquidity_proxy(self, 
                                   close: pd.Series, 
                                   volume: pd.Series, 
                                   high: pd.Series, 
                                   low: pd.Series) -> pd.Series:
        """
        Inverse Amihud Ratio: Volume required to move price 1%.
        High Value = Deep Liquidity (Absorption).
        Low Value = Thin Liquidity (Fragile).
        """
        # Range in percentage terms
        range_pct = (high - low) / close
        
        # Avoid division by zero
        range_pct = range_pct.replace(0, 1e-9)
        
        # Liquidity = Volume / Range
        # We use log to compress the distribution
        liquidity = np.log(volume / range_pct)
        return liquidity

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Main execution pipeline.
        Expects index to be DatetimeIndex.
        Expects columns: ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        df = data.copy()
        
        # 1. Structural Displacement (Rank)
        # "Where is price relative to the last N minutes?" (0.0 to 1.0)
        # Using rolling_rank efficiently
        df['displacement_rank'] = df['Close'].rolling(self.lookback).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )
        
        # 2. Volatility Regime (Raw)
        df['raw_vol'] = self._calculate_parkinson_vol(df['High'], df['Low'])
        
        # 3. Liquidity Stress (Raw)
        df['raw_liq'] = self._calculate_liquidity_proxy(df['Close'], df['Volume'], df['High'], df['Low'])
        
        # 4. Normalization (The "Context" Layer)
        # We normalize Vol and Liq by their Time-of-Day expectations
        # This prevents the model from thinking "Asian Session" is always "Low Volatility Regime"
        df['rel_vol'] = self._normalize_seasonality(df, 'raw_vol')
        df['rel_liq'] = self._normalize_seasonality(df, 'raw_liq')
        
        # 5. Volatility / Liquidity Ratio (The "Fragility" Signal)
        # High Vol + Low Liq = High Fragility (Trend Risk) -> DO NOT REVERT
        # Low Vol + High Liq = Absorption (Range) -> REVERT
        df['fragility_idx'] = df['rel_vol'] / df['rel_liq']
        
        # 6. Clean and Forward Fill
        df.dropna(inplace=True)
        
        # Select Feature Vector for the Classifier
        features = df[[
            'displacement_rank', # State: Overbought/Oversold
            'rel_vol',           # State: Energy
            'rel_liq',           # State: Cushion
            'fragility_idx'      # Derived: Panic Factor
        ]]
        
        return features

# --- Usage Example ---
if __name__ == "__main__":
    # Generate dummy OHLCV data for demonstration
    dates = pd.date_range(start="2024-01-01", periods=1000, freq="1min")
    dummy_data = pd.DataFrame({
        'Open': np.random.normal(1.1000, 0.0005, 1000).cumsum(),
        'Volume': np.random.randint(100, 1000, 1000)
    }, index=dates)
    dummy_data['High'] = dummy_data['Open'] + 0.0002
    dummy_data['Low'] = dummy_data['Open'] - 0.0002
    dummy_data['Close'] = dummy_data['Open'] + np.random.normal(0, 0.0001, 1000)
    
    # Initialize and Run
    engineer = NPLRFeatureEngineer(lookback_window=60)
    feature_vector = engineer.process(dummy_data)
    
    print("Feature Vector Head:")
    print(feature_vector.head())
    
    print("\nInterpretation:")
    print(f"Row 1 Fragility: {feature_vector['fragility_idx'].iloc[0]:.4f}")
    print("If Fragility > 1.5 -> Market is thin and volatile (STOP TRADING).")
    print("If Fragility < 0.8 -> Market is absorbing flow (LOOK FOR REVERSION).")