# HSLR Frontend Architecture
Institutional Monitoring & Control Interface

---

# 1. Overview

The frontend is a real-time monitoring and governance dashboard.

It does NOT generate signals.
It visualizes:

- Regime states
- Edge metrics
- Risk exposure
- Execution health
- Drift statistics
- News overrides

Built with:

- Next.js
- React
- React Flow (DAG visualization)
- Zustand (state management)
- Tailwind CSS

---

# 2. Folder Structure

frontend/
│
├── app/
│   ├── page.tsx
│
├── components/
│   ├── SystemGraph.tsx
│   ├── RegimePanel.tsx
│   ├── EdgePanel.tsx
│   ├── RiskDashboard.tsx
│   ├── NewsPanel.tsx
│   ├── GovernancePanel.tsx
│
├── store/
│   ├── useSystemStore.ts
│
├── services/
│   ├── api.ts
│
├── styles/
│
└── README.md

---

# 3. Core Views

---

## 3.1 System Graph (DAG View)

Displays:

Data → Features → Regime → News → Edge → Risk → Execution → Governance

Each node shows:

- Status (Green/Yellow/Red)
- Latency
- Last update timestamp
- Current metric summary

Allows quick failure detection.

---

## 3.2 Regime Panel

Displays:

- Probability bars
- Entropy value
- Tradeable flag
- Historical regime timeline
- Session ID

Highlights entropy spikes.

---

## 3.3 Edge Analytics Panel

Displays:

- Expected return
- Win probability
- CVaR
- Estimated cost
- Spread state
- Displacement percentile

Shows pass/fail gating logic.

---

## 3.4 Risk Dashboard

Displays:

- Current equity curve
- Drawdown %
- High-water mark
- Position sizes
- Volatility target
- Allocation scaling factor

Includes throttle state indicator.

---

## 3.5 News Monitor

Displays:

- Upcoming events
- Impact level
- Surprise magnitude
- Override active badge
- Event countdown timer

---

## 3.6 Governance Panel

Displays:

- Rolling 30-day IC chart
- KL divergence plot
- Entropy rolling chart
- Allocation reduction factor
- Kill switch status

---

# 4. State Management

Global store holds:

- Regime probabilities
- Entropy
- Signal metrics
- Risk metrics
- Governance metrics
- News override state
- Execution health

Updates via WebSocket from backend.

---

# 5. API Layer

Backend exposes:

GET /regime
GET /edge
GET /risk
GET /governance
GET /news
GET /execution
WS /stream

WebSocket provides live updates.

---

# 6. UI Philosophy

- Minimalist institutional aesthetic
- No decorative clutter
- Color coding strictly functional
- Red only for critical
- Yellow for warning
- Green for operational

---

# 7. Governance Decision Tree (Frontend View)

IF entropy high → show "Uncertain Regime"
IF news override active → show "Event Risk Mode"
IF IC degraded → show "Allocation Reduced"
IF kill switch → show "Execution Halted"

UI must clearly indicate WHY trading is disabled.

---

# 8. Performance Requirements

- Real-time updates < 200ms
- Smooth chart rendering
- No blocking UI calls
- Optimized React Flow rendering

---

# 9. Deployment

- Hosted on Mac M4 Pro
- Reverse proxy via Nginx
- WebSocket support enabled
- Production build with Next.js

---

# 10. Design Goals

The frontend must:

- Detect crisis early
- Surface entropy spikes
- Visualize alpha decay
- Show execution toxicity
- Prevent silent failures

It is a governance tool, not a trading toy.