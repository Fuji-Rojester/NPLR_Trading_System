'use client';
import { useSystemStore } from '../store/useSystemStore';

export default function NewsPanel() {
    const { newsOverride } = useSystemStore();

    return (
        <div className="p-4 bg-gray-900 text-white rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4">News Monitor</h2>

            <div className="space-y-4">
                <div className="flex justify-between items-center p-2 bg-gray-800 rounded">
                    <span className="text-gray-300">Override Status</span>
                    <span className={`font-bold ${newsOverride ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
                        {newsOverride ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                </div>

                <div className="text-sm text-gray-400 mt-4">
                    <div className="mb-2 font-semibold">Upcoming High Impact:</div>
                    <ul className="space-y-2">
                        <li className="flex justify-between">
                            <span>Non-Farm Payrolls</span>
                            <span className="text-yellow-500">2h 15m</span>
                        </li>
                        <li className="flex justify-between text-gray-600">
                            <span>FOMC Minutes</span>
                            <span>Tomorrow</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
