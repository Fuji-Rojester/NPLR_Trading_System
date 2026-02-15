import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        # In a real implementation, we'd client init here (e.g., ForexFactory, Bloomberg, etc.)
        self.events_cache = []
        self._load_mock_calendar()

    def _load_mock_calendar(self):
        """
        Load mock economic calendar for testing/development.
        """
        # Mock events: High impact USD news
        now = datetime.now()
        self.events_cache = [
            {
                "title": "Non-Farm Payrolls",
                "currency": "USD",
                "impact": "High",
                "timestamp": now + timedelta(hours=2) # 2 hours from now
            },
            {
                "title": "FOMC Meeting Minutes",
                "currency": "USD",
                "impact": "High",
                "timestamp": now + timedelta(days=1)
            }
        ]

    def check_high_impact_event(self, pair: str, current_time: datetime = None) -> bool:
        """
        Check if there is a high-impact event for the pair's currencies
        within the window [T-30m, T+60m].
        """
        if current_time is None:
            current_time = datetime.now()
            
        # Parse currencies from pair (e.g., "EURUSD" -> ["EUR", "USD"])
        # Simple parsing assumption: first 3 chars vs last 3 chars
        currencies = [pair[:3], pair[3:]]
        
        # Window
        start_window = current_time - timedelta(minutes=30)
        end_window = current_time + timedelta(minutes=60)
        
        for event in self.events_cache:
            event_time = event["timestamp"]
            
            # Check if event is relevant to pair
            if event["currency"] not in currencies:
                continue
                
            # Check impact
            if event["impact"] != "High":
                continue
                
            # Check window
            if start_window <= event_time <= end_window:
                logger.warning(f"High Impact Event Detected: {event['title']} at {event_time}")
                return True
                
        return False

if __name__ == "__main__":
    service = NewsService()
    # Mock an event happenning now
    service.events_cache.append({
        "title": "Test Event", 
        "currency": "USD", 
        "impact": "High", 
        "timestamp": datetime.now()
    })
    
    print(f"Override Active: {service.check_high_impact_event('EURUSD')}")
