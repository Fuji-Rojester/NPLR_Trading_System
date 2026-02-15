'use client';
import { useSystemStore } from '../store/useSystemStore';

export default function RiskDashboard() {
    const { risk } = useSystemStore();

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4">Risk Dashboard</h2>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h3 className="text-sm text-gray-400">Equity</h3>
                    <div className="text-2xl font-mono">${risk.equity.toLocaleString()}</div>
                </div>

                <div>
                    <h3 className="text-sm text-gray-400">Current Drawdown</h3>
                    <div className={`text-2xl font-mono ${risk.drawdown > 0.05 ? 'text-red-500' : 'text-green-400'}`}>
                        {(risk.drawdown * 100).toFixed(2)}%
                    </div>
                </div>

                <div>
                    <h3 className="text-sm text-gray-400">Volatility (Ann.)</h3>
                    <div className="text-xl font-mono">{(risk.volatility * 100).toFixed(1)}%</div>
                </div>

                <div>
                    <h3 className="text-sm text-gray-400">Position Size</h3>
                    <div className="text-xl font-mono">{risk.position_size.toFixed(2)} units</div>
                </div>
            </div>
        </div>
    );
}
