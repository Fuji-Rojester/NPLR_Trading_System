# HSLR Implementation & Validation Guide
Hybrid Structural Liquidity Reversion System
Institutional Production Blueprint

---

# 1. Objective

This document defines:

- Full backend implementation plan
- Full frontend implementation plan
- Testing & validation framework
- Crisis simulation matrix
- Deployment validation checklist
- Hardware optimization strategy

This system must survive:
- 2008 structural break
- March 2020 liquidity crisis
- Spread shocks
- Execution toxicity
- Alpha decay

The system does NOT assume stationarity.

---

# 2. Backend Implementation

---

# 2.1 Data Service

## Responsibilities
- Ingest 1-min OHLCV
- Capture bid/ask spread
- Store tick velocity
- Batch insert into PostgreSQL
- Cache latest state in Redis

## Implementation Pattern

- Async ingestion loop
- Minute aggregation buffer
- Batch DB writes
- Redis hot snapshot

## Required Checks

- Missing tick detection
- Duplicate timestamp protection
- Out-of-order correction
- Spread = 0 handling
- DB reconnect fallback
- Redis reconnect fallback

Failure mode must degrade safely.

---

# 2.2 Feature Engineering

## Compute

- Log returns
- Garman-Klass volatility
- Spread widening factor
- Displacement percentile
- Cross-pair rolling correlation
- Session-normalized volatility

## Implementation Requirements

- Incremental rolling window updates
- No forward-looking leakage
- Feature validation schema
- NaN prevention

## Tests

- Rolling stability across regime shifts
- Correlation matrix symmetry
- No feature drift under static data
- March 2020 replay integrity

---

# 2.3 Regime Classifier

## Model

RandomForestClassifier

## Outputs

- Probability vector
- Entropy
- Tradeable flag

Trade only if:

P(Stable_Flow) > threshold
AND
Entropy < threshold

## Entropy Logic

Entropy = -Σ p log(p)

High entropy blocks trading during uncertain classification states.
This prevents crisis overtrading.

## Tests

- Probabilities sum to 1
- Entropy spikes in volatility crisis
- No classification lag
- Stable regime produces low entropy

---

# 2.4 Edge Engine (Non-Parametric)

## Model

- KDE OR
- KNN conditional sampling

Conditioned on:

- Displacement percentile
- Volatility state
- Liquidity stress
- Session ID

## Trade Gate

ExpectedReturn > Cost × SafetyFactor  
WinProb > 0.55  
CVaR acceptable  

## Tests

- Shuffle test collapses alpha
- Edge degrades in high-vol regimes
- Spread widened 300% → trades reduce
- Outlier conditioning robustness

---

# 2.5 OU Governance Layer

## Estimate

dX = θ(μ − X)dt + σdW

Half-life = ln(2)/θ

## Purpose

- Exit timing
- Slow reversion detection
- Governance layer only

OU does NOT generate entries.

## Tests

- Theta ≈ 0 detection
- Half-life explosion under crisis
- No division errors
- Stable estimation under noise

---

# 2.6 News Override

## Pull

- Event time
- Impact level
- Currency
- Forecast
- Actual
- Historical surprise std

## Event Window

[T_event - 30m, T_event + 60m]

If High Impact + Currency Match → Disable trading.

## Optional

Standardized surprise detection for temporary directional mode.

## Tests

- Window alignment accuracy
- Surprise computation correctness
- API outage fallback
- Override resets correctly

---

# 2.7 Risk & Portfolio Engine

## Utility

U = E[R] - λVar(R) - Cost(Turnover)

## Controls

- Vol targeting
- Drawdown throttle
  >3% → -50%
  >5% → -75%
- High-water mark
- Allocation scaling

## Tests

- Drawdown logic integrity
- Equity curve correctness
- No overexposure
- Position flip stability

---

# 2.8 Execution Router

## Rules

- Limit inside spread
- Cancel if regime invalidates
- Monitor adverse selection

Adverse Selection Ratio:
(Price after 1s − Fill price)

Persistent toxicity → Kill switch

## Tests

- Partial fill handling
- Slippage monitoring
- 200ms latency injection
- Toxicity trigger validation

---

# 2.9 Drift Monitor

## Metrics

1) Rolling 30-day IC  
2) KL divergence  
3) Regime entropy average  

## Triggers

IC < 0.02 for 2 weeks → reduce 50%  
IC < 0 for 4 weeks → decommission  
KL spike → halt & retrain  
Persistent entropy spike → suspend  

## Tests

- IC degradation detection
- KL divergence spike detection
- No false positives in stable regime
- Crisis replay validation

---

# 3. Frontend Implementation

---

# 3.1 Core Stack

- Next.js
- TypeScript
- React Flow
- Zustand
- Tailwind
- WebSocket streaming

---

# 3.2 WebSocket Architecture

Backend pushes:

{
  regime,
  edge,
  risk,
  governance,
  news,
  execution
}

Frontend updates global store.

No polling.

---

# 3.3 Core Components

---

## System Graph (DAG)

Displays pipeline:

Data → Features → Regime → News → Edge → Risk → Execution → Governance

Node states:
Green = OK  
Yellow = Warning  
Red = Halt  

Test:
- Correct state transitions
- No unnecessary re-renders

---

## Regime Panel

Displays:
- Probabilities
- Entropy
- Tradeable flag
- Timeline

Test:
- Entropy spike visualization
- Instant tradeable update

---

## Edge Panel

Displays:
- Expected return
- Win probability
- CVaR
- Cost comparison

Test:
- Values consistent with backend
- Gating logic visible

---

## Risk Dashboard

Displays:
- Equity curve
- Drawdown %
- Allocation scaling
- Position sizes

Test:
- Real-time smooth rendering
- No blocking UI

---

## Governance Panel

Displays:
- IC chart
- KL divergence plot
- Entropy rolling
- Kill switch status

Test:
- Crisis replay accuracy
- Allocation reduction visible

---

## News Panel

Displays:
- Upcoming events
- Countdown
- Override badge

Test:
- Event window alignment
- Surprise magnitude display

---

# 4. System-Wide Validation Framework

---

# 4.1 Regime Stratification Test

Sharpe by regime:

Stable_Flow → positive  
Directional_Vol → flat  
Event_Risk → near zero  

If not → classifier failure.

---

# 4.2 Shuffle Test

Randomize returns.

Expected:
Sharpe collapses.

If not → leakage.

---

# 4.3 Monte Carlo Spread Shock

Increase spread 300%.

Expected:
Trade frequency drops.
Sharpe survives.

---

# 4.4 Latency Injection

Inject 200ms delay.

Expected:
Minor degradation only.

---

# 4.5 March 2020 Replay

Expected:
Entropy spikes.
Regime shifts.
Trading mostly disabled.
Capital preserved.

---

# 4.6 2008 Crisis Replay

Expected:
Extended suspension.
No overtrading.
Limited drawdown.

---

# 5. Failure Simulation Matrix

Simulate:

- Database outage
- Redis crash
- News API failure
- Spread spike
- Correlation breakdown
- Model artifact corruption
- Feature corruption
- Execution venue rejection

System must fail safely.

---

# 6. Deployment Validation Checklist

Before going live:

- All modules respond
- Model version validated
- IC positive
- KL within range
- Entropy stable
- Spread normal
- News override tested
- Execution sandbox verified
- Kill switch manually tested
- Log pipeline operational

---

# 7. Hardware Optimization

---

## MacBook M4 Pro (Live)

- Async services
- uvloop enabled
- 2–4 workers max
- Redis for hot cache
- Memory < 12GB steady state

---

## i7 + RTX 4070 (Research)

- Parallel walk-forward
- Monte Carlo in parallel
- KDE bandwidth tuning
- Hyperparameter search
- Artifact versioning

---

# 8. Crisis Protection Summary

System survives crises because:

- It monitors entropy
- It monitors alpha decay
- It monitors distribution drift
- It blocks trading during uncertainty
- It reduces allocation under stress
- It kills execution under toxicity
- It does not assume stationarity

---

# 9. Build Order Recommendation

1. Data pipeline
2. Feature engineering
3. Regime classifier
4. Backtest framework
5. Edge engine
6. Risk layer
7. News override
8. Drift monitor
9. Frontend
10. Execution router

---

End of Implementation & Validation Guide.