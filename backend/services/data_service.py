import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import asyncpg
import redis.asyncio as redis
from backend.app.config import settings

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        
    async def connect(self):
        """Initialize DB and Redis connections."""
        try:
            self.redis_client = await redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            self.db_pool = await asyncpg.create_pool(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT
            )
            logger.info("Connected to DB and Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to services: {e}")
            raise

    async def ingest_ohlcv(self, pair: str, data: Dict):
        """
        Ingest a single OHLCV data point.
        Data format: {timestamp, open, high, low, close, volume}
        """
        try:
            # 1. Cache latest state in Redis
            await self.redis_client.set(f"price:{pair}", json.dumps(data))
            
            # 2. Push to batch queue (implemented as a list in Redis for simplicity or internal buffer)
            # For robustness, we might want to write directly or use a buffer. 
            # Here we'll implement a direct write for simplicity, but in production, we'd batch.
            await self.write_ohlcv_to_db(pair, data)
            
        except Exception as e:
            logger.error(f"Error ingesting OHLCV for {pair}: {e}")

    async def write_ohlcv_to_db(self, pair: str, data: Dict):
        """Write a single OHLCV record to DB."""
        if not self.db_pool:
            logger.error("DB pool not initialized.")
            return

        query = """
            INSERT INTO price_data (pair, timestamp, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (pair, timestamp) DO NOTHING;
        """
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    pair,
                    datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
                    data['open'],
                    data['high'],
                    data['low'],
                    data['close'],
                    data['volume']
                )
        except Exception as e:
            logger.error(f"DB Write Error: {e}")

    async def get_latest_price(self, pair: str) -> Optional[Dict]:
        """Get latest price from Redis."""
        if not self.redis_client:
            return None
        data = await self.redis_client.get(f"price:{pair}")
        return json.loads(data) if data else None

    async def close(self):
        """Close connections."""
        if self.redis_client:
            await self.redis_client.close()
        if self.db_pool:
            await self.db_pool.close()
        logger.info("Connections closed.")
