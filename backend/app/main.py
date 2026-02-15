import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.services.feature_service import FeatureService
from backend.services.regime_service import RegimeService
from backend.services.edge_engine import EdgeEngine
from backend.services.risk_service import RiskService
from backend.services.news_service import NewsService
from backend.services.drift_monitor import DriftMonitor
# from backend.services.execution_router import ExecutionRouter # To be implemented

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HSLR_System")

# Initialize Services
feature_service = FeatureService()
regime_service = RegimeService()
edge_engine = EdgeEngine()
risk_service = RiskService()
news_service = NewsService()
drift_monitor = DriftMonitor()

# Global State for Simulation
connected_clients = []

class SimulationState:
    def __init__(self):
        self.pair = "EURUSD"
        self.prices = [1.1000] * 50
        self.vol_mult = 1.0

sim_state = SimulationState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start simulation loop
    task = asyncio.create_task(run_simulation_loop())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "change_pair":
                    new_pair = message.get("payload", {}).get("pair")
                    if new_pair and new_pair != sim_state.pair:
                        sim_state.pair = new_pair
                        # Reset prices based on pair roughly
                        start_price = 100.0
                        if "JPY" in new_pair: start_price = 150.0
                        if "BTC" in new_pair: start_price = 65000.0
                        if "EUR" in new_pair: start_price = 1.10
                        if "GBP" in new_pair: start_price = 1.25
                        
                        sim_state.prices = [start_price] * 50
                        logger.info(f"Switched pair to {new_pair}")
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast(message: dict):
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"WS Send Error: {e}")
            pass

async def run_simulation_loop():
    """
    Simulates the 1-minute data pipeline loop.
    """
    logger.info("Starting Simulation Loop...")
    
    while True:
        try:
            # 1. Generate Synthetic Data Point (Random Walk)
            prev_price = sim_state.prices[-1]
            # Adjust volatility based on price level
            vol = 0.0005 * prev_price 
            change = np.random.normal(0, vol) 
            price = prev_price + change
            sim_state.prices.append(price)
            if len(sim_state.prices) > 100: sim_state.prices.pop(0)
            
            # Construct DataFrame for services (single row + history)
            # In real system, we'd fetch history from DB/Redis
            df = pd.DataFrame({
                'close': sim_state.prices,
                'open': [p - (0.0002*p) for p in sim_state.prices], # Mock
                'high': [p + (0.0005*p) for p in sim_state.prices],
                'low': [p - (0.0005*p) for p in sim_state.prices],
                'spread': [0.0001 * p for p in sim_state.prices],
                'volume': [1000] * len(sim_state.prices)
            })
            
            # 2. Pipeline Execution
            
            # Feature Engineering
            df = feature_service.process_features(df)
            current_features = df.iloc[[-1]] # Last row as DataFrame
             
            # Regime Classification
            # The dummy model was trained on 5 features (from make_classification).
            # The feature service produces: log_return, gk_vol, spread_factor, displacement_pct, session_vol (and original cols).
            # We select 5 numeric features to feed the dummy model.
            
            model_features = current_features[['log_return', 'gk_vol', 'spread_factor', 'displacement_pct', 'session_vol']].fillna(0)
            
            # Ensure we have exactly 5 columns and values
            if model_features.shape[1] < 5:
                # If for some reason cols missing, pad
                pass
                
            regime_result = regime_service.predict_regime(model_features)
            
            # News Override
            if news_service.check_high_impact_event(sim_state.pair):
                regime_result['tradeable'] = False
                regime_result['override_active'] = True
                await broadcast({"type": "news", "payload": {"active": True}})
            else:
                await broadcast({"type": "news", "payload": {"active": False}})

            await broadcast({"type": "regime", "payload": regime_result})
            await broadcast({"type": "price", "payload": {"pair": sim_state.pair, "price": price}})

            
            # Edge Engine
            signal = edge_engine.predict_signal(current_features, regime_result)
            if signal:
                await broadcast({"type": "edge", "payload": signal})
            else:
                # Send null or empty to clear? Or just don't send?
                # Frontend handles null, let's send null to reset UI if needed or keep last.
                # Ideally we want to show 'No Signal'
                await broadcast({"type": "edge", "payload": None})
                
            # Risk Layer
            # Update equity with simulated PnL if we had a position (mocking logic)
            # Mock PnL: random small fluctuation
            current_equity = risk_service.equity + np.random.normal(0, 5) # Larger equity swings
            risk_service.update_equity(current_equity)
            
            # Calculate position size for next trade
            current_vol = current_features['session_vol'].iloc[-1]
            size = risk_service.calculate_position_size(signal, price, current_vol)
            
            risk_payload = {
                "equity": risk_service.equity,
                "drawdown": risk_service.current_drawdown,
                "position_size": size,
                "volatility": current_vol if not np.isnan(current_vol) else 0.0
            }
            await broadcast({"type": "risk", "payload": risk_payload})
            
            # Governance / Drift
            # Mocking drift updates
            drift_monitor.update(0.001, 0.001 + np.random.normal(0, 0.0001), regime_result['entropy'])
            governance_payload = {
                "ic": drift_monitor.calculate_ic(),
                "kl_divergence": np.abs(np.random.normal(0, 0.1)), # Mock KL
                "entropy_avg": drift_monitor.calculate_entropy_avg()
            }
            await broadcast({"type": "governance", "payload": governance_payload})
            
            logger.info(f"Step Complete. Pair: {sim_state.pair}, Price: {price:.4f}, Regime: {regime_result['tradeable']}")
            
            # Sleep (Simulate 1-minute candles sped up to 2 seconds for demo)
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Simulation Error: {e}")
            await asyncio.sleep(2)
