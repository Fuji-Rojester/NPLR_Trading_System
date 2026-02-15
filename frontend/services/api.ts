import { useSystemStore } from '../store/useSystemStore';

class ApiService {
    private socket: WebSocket | null = null;
    private maxRetries = 5;
    private retryCount = 0;

    connect() {
        // Replace with actual backend WS URL
        const WS_URL = 'ws://localhost:8000/ws';

        console.log(`Connecting to WebSocket: ${WS_URL}`);
        this.socket = new WebSocket(WS_URL);

        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.retryCount = 0;
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WS message:', error);
            }
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            this.retryConnection();
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(data: any) {
        // Dispatch to store based on message type
        // Assuming backend sends { type: 'regime', data: ... }

        const store = useSystemStore.getState();

        switch (data.type) {
            case 'regime':
                store.setRegime(data.payload);
                break;
            case 'edge':
                store.setEdge(data.payload);
                break;
            case 'risk':
                useSystemStore.getState().setRisk(data.payload);
                break;
            case 'governance':
                useSystemStore.getState().setGovernance(data.payload);
                break;
            case 'news':
                useSystemStore.getState().setNewsOverride(data.payload.active);
                break;
            case 'price':
                useSystemStore.getState().setPrice({ pair: data.payload.pair, value: data.payload.price });
                break;
            default:
            // console.warn('Unknown message type:', data.type);
        }
    }

    retryConnection() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`Retrying connection in ${this.retryCount * 1000}ms...`);
            setTimeout(() => this.connect(), this.retryCount * 1000);
        } else {
            console.error('Max WS retries reached.');
        }
    }

    sendMessage(type: string, payload: any) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type, payload }));
        } else {
            console.warn('WebSocket not open. Cannot send message.');
        }
    }
}

export const apiService = new ApiService();
