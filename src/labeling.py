import numpy as np
import pandas as pd

class BarrierLabeler:
    """
    Implements the Triple Barrier Method to label historical data.
    Goal: Identify 'Safe' mean-reversion opportunities.
    """
    def __init__(self, profit_thresh=0.0005, stop_thresh=0.0005, horizon=15):
        self.pt = profit_thresh
        self.sl = stop_thresh
        self.horizon = horizon

    def apply(self, close_prices):
        """
        Returns a binary Series: 
        1 = Reversion Successful (Price moved opposite to recent move & hit target).
        0 = Reversion Failed (Trended or chopped).
        """
        labels = []
        prices = close_prices.values
        
        for i in range(len(prices) - self.horizon):
            current_price = prices[i]
            # Recent direction (simple 1-bar lookback for context)
            # In production, link this to the 'displacement' feature direction
            direction = np.sign(prices[i] - prices[i-1]) if i > 0 else 0
            
            if direction == 0: 
                labels.append(0)
                continue

            # Look forward 'horizon' bars
            future_window = prices[i+1 : i+1+self.horizon]
            
            # Calculate returns relative to current price
            returns = (future_window - current_price) / current_price
            
            # IF we are Long (Direction was Down, we want Reversion UP)
            if direction < 0:
                # Did we hit PT?
                hit_pt = np.any(returns >= self.pt)
                # Did we hit SL?
                hit_sl = np.any(returns <= -self.sl)
                
                # Success = Hit PT before SL (or Hit PT and didn't hit SL)
                # Ideally: Check timestamps of hit. Simplified: If SL hit, it's unsafe.
                if hit_pt and not hit_sl:
                    labels.append(1)
                else:
                    labels.append(0)

            # IF we are Short (Direction was Up, we want Reversion DOWN)
            elif direction > 0:
                hit_pt = np.any(returns <= -self.pt)
                hit_sl = np.any(returns >= self.sl)
                
                if hit_pt and not hit_sl:
                    labels.append(1)
                else:
                    labels.append(0)
                    
        # Pad the end
        labels.extend([0] * self.horizon)
        return pd.Series(labels, index=close_prices.index)