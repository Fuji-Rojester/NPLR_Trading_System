'use client';
import { useSystemStore } from '../store/useSystemStore';

export default function GovernancePanel() {
    const { governance } = useSystemStore();

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4">Governance Monitor</h2>

            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <span className="text-gray-400">Information Coeff (IC)</span>
                    <span className={`font-mono ${governance.ic < 0.02 ? 'text-red-400' : 'text-green-400'}`}>
                        {governance.ic.toFixed(4)}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-gray-400">KL Divergence</span>
                    <span className={`font-mono ${governance.kl_divergence > 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                        {governance.kl_divergence.toFixed(4)}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-gray-400">Entropy (Avg)</span>
                    <span className="font-mono">{governance.entropy_avg.toFixed(4)}</span>
                </div>
            </div>
        </div>
    );
}
