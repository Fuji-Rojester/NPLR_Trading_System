'use client';
import { useSystemStore } from '../store/useSystemStore';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function RegimePanel() {
    const { regime } = useSystemStore();

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4">Regime Classifier</h2>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h3 className="text-sm text-gray-400">Current State</h3>
                    <div className={`text-2xl font-mono ${regime.tradeable ? 'text-green-400' : 'text-red-400'}`}>
                        {regime.tradeable ? 'TRADEABLE' : 'BLOCKED'}
                    </div>
                </div>

                <div>
                    <h3 className="text-sm text-gray-400">Entropy</h3>
                    <div className="text-2xl font-mono">{regime.entropy.toFixed(4)}</div>
                </div>
            </div>

            <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                    <span>Stable Flow</span>
                    <span>{(regime.prob_stable * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div className="bg-blue-500 h-full" style={{ width: `${regime.prob_stable * 100}%` }} />
                </div>

                <div className="flex justify-between text-sm">
                    <span>Directional Vol</span>
                    <span>{(regime.prob_directional * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div className="bg-yellow-500 h-full" style={{ width: `${regime.prob_directional * 100}%` }} />
                </div>

                <div className="flex justify-between text-sm">
                    <span>Event Risk</span>
                    <span>{(regime.prob_event * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div className="bg-red-500 h-full" style={{ width: `${regime.prob_event * 100}%` }} />
                </div>
            </div>
        </div>
    );
}
