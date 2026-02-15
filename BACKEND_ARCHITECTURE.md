# HSLR Backend Architecture
Hybrid Structural Liquidity Reversion System
Production-Grade Quant Infrastructure

---

# 1. System Overview

The backend is designed as a modular, crisis-resilient microservice architecture.

It separates:

- Alpha Logic
- Risk Logic
- Governance Logic
- News Override Logic
- Execution Logic

The system is designed for:

- Live trading on MacBook M4 Pro (24GB RAM)
- Model training on i7 + RTX 4070 machine
- Walk-forward validation
- Crisis survival (2008 / 2020 style)

---

# 2. Service Architecture (DAG)

Market Data
    ↓
Feature Engineering
    ↓
Regime Classifier
    ↓
News Override
    ↓
Edge Engine
    ↓
Risk Engine
    ↓
Execution Router
    ↓
PnL & Portfolio Update
    ↓
Governance & Drift Monitor

Each module is independently deployable.

---

# 3. Folder Structure

backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│
├── services/
│   ├── data_service.py
│   ├── feature_service.py
│   ├── regime_service.py
│   ├── edge_engine.py
│   ├── ou_governance.py
│   ├── news_service.py
│   ├── risk_service.py
│   ├── execution_router.py
│   ├── drift_monitor.py
│
├── models/
│   ├── regime_model.joblib
│   ├── kde_model.joblib
│
├── db/
│   ├── schema.sql
│   ├── migrations/
│
├── backtesting/
│   ├── walk_forward.py
│   ├── monte_carlo.py
│   ├── shuffle_test.py
│   ├── latency_sim.py
│
├── logs/
│
├── docker-compose.yml
├── requirements.txt
└── README.md

---

# 4. Data Layer

## Database: PostgreSQL (TimescaleDB recommended)

Tables:

price_data(
    pair TEXT,
    timestamp TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT
)

spread_data(
    pair TEXT,
    timestamp TIMESTAMP,
    spread FLOAT
)

features(
    pair TEXT,
    timestamp TIMESTAMP,
    feature_vector JSONB
)

regime_output(
    pair TEXT,
    timestamp TIMESTAMP,
    prob_stable FLOAT,
    prob_directional FLOAT,
    prob_event FLOAT,
    entropy FLOAT,
    tradeable BOOLEAN
)

signals(
    pair TEXT,
    timestamp TIMESTAMP,
    expected_return FLOAT,
    win_prob FLOAT,
    cvar FLOAT
)

positions(
    pair TEXT,
    timestamp TIMESTAMP,
    size FLOAT,
    pnl FLOAT
)

governance_metrics(
    timestamp TIMESTAMP,
    ic FLOAT,
    kl_divergence FLOAT,
    entropy_avg FLOAT
)

---

# 5. Core Modules

---

## 5.1 Data Service

Responsibilities:
- Ingest 1-min OHLCV
- Store spreads
- Cache real-time data in Redis
- Provide streaming API

---

## 5.2 Feature Engineering Service

Computes:

- Log returns
- Garman-Klass volatility
- Spread widening factor
- Tick velocity
- Rolling displacement percentile
- Cross-pair correlation
- Session-normalized volatility

Runs every minute.

---

## 5.3 Regime Classifier

Model: RandomForestClassifier

States:
- Stable_Flow
- Directional_Vol
- Event_Risk

Outputs:
- Probability vector
- Entropy
- Tradeable flag

Trading allowed only if:

P(Stable_Flow) > threshold
AND entropy < threshold

Entropy prevents crisis overtrading by blocking uncertain classification states.

---

## 5.4 Edge Engine (Non-Parametric)

Model:
- KDE or KNN conditional model

Conditioned on:
- Displacement percentile
- Volatility state
- Liquidity stress
- Session ID

Outputs:
- Expected forward return
- Win probability
- Conditional 5% CVaR

Trade only if:

ExpectedReturn > EstimatedCost × SafetyFactor
WinProb > 55%
CVaR within acceptable bounds

---

## 5.5 OU Governance Layer

Estimates:
- Mean reversion speed (theta)
- Half-life = ln(2)/theta

Used for:
- Exit timing
- Detecting slow reversion

OU NEVER generates entries.

---

## 5.6 News Override

Pulls economic calendar via API.

If:
- High impact
- Pair affected
- Within event window

Override regime to Event_Risk.

Optional:
If surprise magnitude exceeds threshold,
activate temporary directional mode.

---

## 5.7 Risk & Portfolio Engine

Utility Function:

U = E[R] - λVar(R) - Cost(Turnover)

Includes:

- Volatility targeting
- Drawdown throttle
    >3% DD → -50% size
    >5% DD → -75% size
- High-water mark logic

No fixed stops alone.

---

## 5.8 Execution Router

Rules:

- Limit orders inside spread
- No market entries
- Cancel if regime invalidates
- Monitor adverse selection

If persistent toxicity:
Kill switch activated.

---

## 5.9 Drift Monitor

Implements:

1) Rolling 30-day IC
2) KL divergence
3) Regime entropy monitor

Triggers:

IC < 0.02 for 2 weeks → reduce allocation
IC < 0 for 4 weeks → decommission
KL divergence spike → halt & retrain
Persistent entropy spike → suspend trading

---

# 6. Research Node (GPU Machine)

Used for:

- Walk-forward validation
- Hyperparameter search
- Monte Carlo spread shocks
- Latency injection tests
- Shuffle tests

Not used for live execution.

---

# 7. Deployment

- Dockerized services
- Model versioning
- Daily artifact backups
- Structured JSON logging
- systemd process supervision

---

# 8. Crisis Survivability Layers

1. Regime shift detection
2. Entropy guard
3. News override
4. Spread shock testing
5. IC degradation monitor
6. OU half-life governance
7. Toxicity kill switch

System does NOT assume stationarity.

---

# 9. Hardware Allocation

Mac M4 Pro:
- Live trading
- Feature engineering
- Inference
- DB + Redis
- Frontend hosting

i7 + 4070:
- Model training
- Stress simulations
- Walk-forward
- KDE optimization