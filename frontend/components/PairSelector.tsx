'use client';
import { useSystemStore } from '../store/useSystemStore';
import { apiService } from '../services/api';

const PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'ETHUSD'];

export default function PairSelector() {
    const { selectedPair, setSelectedPair, price } = useSystemStore();

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newPair = e.target.value;
        setSelectedPair(newPair);
        apiService.sendMessage('change_pair', { pair: newPair });
    };

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Market Selection</h2>
                <div className="text-right">
                    <div className="text-2xl font-mono text-blue-400">
                        {price && price.value ? price.value.toFixed(price.pair.includes('JPY') || price.pair.includes('BTC') ? 2 : 4) : '---'}
                    </div>
                    <div className="text-xs text-gray-500">{price?.pair || '---'}</div>
                </div>
            </div>
            <div className="flex flex-col space-y-2">
                <label htmlFor="pair-select" className="text-sm text-gray-400">Trading Pair</label>
                <select
                    id="pair-select"
                    value={selectedPair}
                    onChange={handleChange}
                    className="bg-gray-800 text-white border border-gray-700 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    {PAIRS.map(pair => (
                        <option key={pair} value={pair}>{pair}</option>
                    ))}
                </select>
                <div className="text-xs text-gray-500 mt-2">
                    Switching pairs resets the simulation context.
                </div>
            </div>
        </div>
    );
}
