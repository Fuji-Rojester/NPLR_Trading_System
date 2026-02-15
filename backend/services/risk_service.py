import logging
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RiskService:
    def __init__(self, initial_equity: float = 10000.0, vol_target: float = 0.15):
        self.equity = initial_equity
        self.high_water_mark = initial_equity
        self.vol_target = vol_target
        self.current_drawdown = 0.0
        
    def update_equity(self, current_equity: float):
        """Update equity and calculate drawdown."""
        self.equity = current_equity
        if self.equity > self.high_water_mark:
            self.high_water_mark = self.equity
        
        if self.high_water_mark > 0:
            self.current_drawdown = (self.high_water_mark - self.equity) / self.high_water_mark
        else:
            self.current_drawdown = 0.0

    def get_drawdown_modifier(self) -> float:
        """
        Calculate size modifier based on drawdown.
        >3% DD -> 0.5
        >5% DD -> 0.25
        """
        if self.current_drawdown > 0.05:
            logger.warning(f"Drawdown {self.current_drawdown:.2%} > 5%. Throttling size to 25%.")
            return 0.25
        elif self.current_drawdown > 0.03:
            logger.warning(f"Drawdown {self.current_drawdown:.2%} > 3%. Throttling size to 50%.")
            return 0.50
        return 1.0

    def calculate_position_size(self, signal: Dict, price: float, volatility: float) -> float:
        """
        Calculate position size using Volatility Targeting and Drawdown Throttling.
        Size = (Equity * VolTarget) / (Price * Volatility) * Modifier
        """
        if not signal:
            return 0.0
            
        # Volatility usually in annual terms or needs scaling. 
        # Assuming volatility is daily std dev here for simplicity of example formula, 
        # or we scale accordingly.
        # If vol is minute vol, we scale to daily/annual to match target.
        # Let's assume vol_target is annual 0.15 (15%).
        # And input volatility is annual as well for now or we convert.
        # For safety in this MVP, we essentially do inverse volatility weighting.
        
        # Guard against zero vol
        if volatility <= 1e-6:
            logger.warning("Volatility too low, defaulting to min size.")
            volatility = 0.01

        # Base Size (Kelly-like or Vol Target)
        # Using Vol Target:
        # Target Risk = Equity * Target Vol
        # Position Risk = Size * Price * Volatility
        # Size = (Equity * Target Vol) / (Price * Volatility)
        
        base_size = (self.equity * self.vol_target) / (price * volatility)
        
        # Apply Logic for Drawdown
        modifier = self.get_drawdown_modifier()
        
        final_size = base_size * modifier
        
        logger.info(f"Calculated Size: {final_size} (Base: {base_size}, Mod: {modifier})")
        return final_size

    def calculate_utility(self, expected_return: float, variance: float, cost: float, risk_aversion: float = 1.0) -> float:
        """
        U = E[R] - lambda * Var(R) - Cost
        """
        return expected_return - (risk_aversion * variance) - cost
