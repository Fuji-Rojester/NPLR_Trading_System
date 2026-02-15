import { create } from 'zustand';

interface RegimeData {
    prob_stable: number;
    prob_directional: number;
    prob_event: number;
    entropy: number;
    tradeable: boolean;
    timestamp: string;
}

interface EdgeData {
    expected_return: number;
    win_prob: number;
    cvar: number;
    action: string;
}

interface RiskData {
    equity: number;
    drawdown: number;
    position_size: number;
    volatility: number;
}

interface GovernanceData {
    ic: number;
    kl_divergence: number;
    entropy_avg: number;
}

interface SystemState {
    regime: RegimeData;
    edge: EdgeData | null;
    risk: RiskData;
    governance: GovernanceData;
    newsOverride: boolean;
    selectedPair: string;
    price: { pair: string, value: number };

    setRegime: (data: RegimeData) => void;
    setEdge: (data: EdgeData) => void;
    setRisk: (data: RiskData) => void;
    setGovernance: (data: GovernanceData) => void;
    setNewsOverride: (active: boolean) => void;
    setSelectedPair: (pair: string) => void;
    setPrice: (data: { pair: string, value: number }) => void;
}

export const useSystemStore = create<SystemState>((set) => ({
    regime: {
        prob_stable: 0,
        prob_directional: 0,
        prob_event: 0,
        entropy: 0,
        tradeable: false,
        timestamp: '',
    },
    edge: null,
    risk: {
        equity: 10000,
        drawdown: 0,
        position_size: 0,
        volatility: 0
    },
    governance: {
        ic: 0,
        kl_divergence: 0,
        entropy_avg: 0
    },
    newsOverride: false,
    selectedPair: 'EURUSD',
    price: { pair: 'EURUSD', value: 0 },

    setRegime: (data) => set({ regime: data }),
    setEdge: (data) => set({ edge: data }),
    setRisk: (data) => set({ risk: data }),
    setGovernance: (data) => set({ governance: data }),
    setNewsOverride: (active) => set({ newsOverride: active }),
    setSelectedPair: (pair) => set({ selectedPair: pair }),
    setPrice: (data) => set({ price: data }),
}));
