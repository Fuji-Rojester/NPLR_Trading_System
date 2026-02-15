'use client';
import { ReactFlow, Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';
import { useSystemStore } from '../store/useSystemStore';

const initialNodes = [
    { id: '1', position: { x: 0, y: 100 }, data: { label: 'Data Source' }, style: { background: '#22c55e', color: 'white' } },
    { id: '2', position: { x: 200, y: 100 }, data: { label: 'Feature Eng' }, style: { background: '#22c55e', color: 'white' } },
    { id: '3', position: { x: 400, y: 100 }, data: { label: 'Regime Classifier' }, style: { background: '#22c55e', color: 'white' } },
    { id: '4', position: { x: 400, y: 0 }, data: { label: 'News Override' }, style: { background: '#eab308', color: 'black' } },
    { id: '5', position: { x: 600, y: 100 }, data: { label: 'Edge Engine' }, style: { background: '#ef4444', color: 'white' } },
    { id: '6', position: { x: 800, y: 100 }, data: { label: 'Risk Layer' }, style: { background: '#3b82f6', color: 'white' } },
    { id: '7', position: { x: 1000, y: 100 }, data: { label: 'Execution Router' }, style: { background: '#3b82f6', color: 'white' } },
    { id: '8', position: { x: 800, y: 200 }, data: { label: 'Governance' }, style: { background: '#a855f7', color: 'white' } },
];

const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e2-3', source: '2', target: '3', animated: true },
    { id: 'e3-5', source: '3', target: '5', animated: true },
    { id: 'e4-3', source: '4', target: '3', animated: true, label: 'Override' },
    { id: 'e5-6', source: '5', target: '6', animated: true },
    { id: 'e6-7', source: '6', target: '7', animated: true },
    { id: 'e7-8', source: '7', target: '8', animated: true, type: 'step' },
];

export default function SystemGraph() {
    // Ideally update node colors based on store state
    // For now static layout

    return (
        <div className="h-[300px] w-full bg-gray-900 rounded-lg shadow-lg border border-gray-800">
            <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
                <Background color="#444" gap={16} />
                <Controls />
            </ReactFlow>
        </div>
    );
}
