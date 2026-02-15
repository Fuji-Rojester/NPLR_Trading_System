'use client';
import { useSystemStore } from '../store/useSystemStore';

export default function EdgePanel() {
    const { edge } = useSystemStore();

    if (!edge) {
        return (
            <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg opacity-50">
                <h2 className="text-xl font-bold mb-4">Edge Engine</h2>
                <div className="text-center py-8 text-gray-400">No active signal</div>
            </div>
        )
    }

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg border-l-4 border-green-500">
            <h2 className="text-xl font-bold mb-4">Edge Engine</h2>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h3 className="text-sm text-gray-400">Action</h3>
                    <div className={`text-2xl font-bold ${edge.action === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                        {edge.action}
                    </div>
                </div>
                <div>
                    <h3 className="text-sm text-gray-400">Exp. Return</h3>
                    <div className="text-xl font-mono">{(edge.expected_return * 10000).toFixed(1)} bps</div>
                </div>
                <div>
                    <h3 className="text-sm text-gray-400">Win Prob</h3>
                    <div className="text-xl font-mono">{(edge.win_prob * 100).toFixed(1)}%</div>
                </div>
                <div>
                    <h3 className="text-sm text-gray-400">CVaR (5%)</h3>
                    <div className="text-xl font-mono text-red-300">{(edge.cvar * 100).toFixed(2)}%</div>
                </div>
            </div>
        </div>
    );
}
