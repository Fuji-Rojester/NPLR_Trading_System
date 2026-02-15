-- HSLR Trading System Schema

CREATE TABLE IF NOT EXISTS price_data (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS spread_data (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    spread DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS features (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    feature_vector JSONB NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS regime_output (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    prob_stable DOUBLE PRECISION NOT NULL,
    prob_directional DOUBLE PRECISION NOT NULL,
    prob_event DOUBLE PRECISION NOT NULL,
    entropy DOUBLE PRECISION NOT NULL,
    tradeable BOOLEAN NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS signals (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    expected_return DOUBLE PRECISION NOT NULL,
    win_prob DOUBLE PRECISION NOT NULL,
    cvar DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS positions (
    pair TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    size DOUBLE PRECISION NOT NULL,
    pnl DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (pair, timestamp)
);

CREATE TABLE IF NOT EXISTS governance_metrics (
    timestamp TIMESTAMP NOT NULL,
    ic DOUBLE PRECISION NOT NULL,
    kl_divergence DOUBLE PRECISION NOT NULL,
    entropy_avg DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (timestamp)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_spread_timestamp ON spread_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_features_timestamp ON features(timestamp DESC);
