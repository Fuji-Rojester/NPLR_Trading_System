'use client';
import { useEffect } from 'react';
import { apiService } from '@/services/api';
import SystemGraph from '@/components/SystemGraph';
import RegimePanel from '@/components/RegimePanel';
import EdgePanel from '@/components/EdgePanel';
import RiskDashboard from '@/components/RiskDashboard';
import GovernancePanel from '@/components/GovernancePanel';
import NewsPanel from '@/components/NewsPanel';
import PairSelector from '@/components/PairSelector';

export default function Home() {
  useEffect(() => {
    // Connect to WebSocket on mount
    apiService.connect();
  }, []);

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <header className="mb-8 border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-gray-100">HSLR Trading System</h1>
        <p className="text-gray-400 mt-2">Hybrid Structural Liquidity Reversion • Institutional Production Dashboard</p>
      </header>

      <div className="grid grid-cols-12 gap-6">
        {/* Top Row: System Health (DAG) */}
        <div className="col-span-12 xl:col-span-8">
          <div className="mb-2 text-sm text-gray-400 uppercase tracking-widest">System Architecture</div>
          <SystemGraph />
        </div>

        {/* Top Row: Key Metrics / Governance */}
        <div className="col-span-12 xl:col-span-4 space-y-6">
          <div className="p-4 bg-gray-900 rounded-lg">
            <h3 className="font-bold mb-2">System Status</h3>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span>Operational</span>
            </div>
            <div className="mt-4 text-sm text-gray-400">
              Host: M4 Pro (Local)<br />
              Latency: 12ms
            </div>
          </div>
          <PairSelector />
          <NewsPanel />
        </div>

        {/* Second Row: Detailed Panels */}
        <div className="col-span-12 md:col-span-4">
          <RegimePanel />
        </div>
        <div className="col-span-12 md:col-span-4">
          <EdgePanel />
        </div>
        <div className="col-span-12 md:col-span-4">
          <RiskDashboard />
        </div>

        {/* Third Row: Governance */}
        <div className="col-span-12">
          <GovernancePanel />
        </div>
      </div>
    </main>
  );
}
