import os
import redis.asyncio as redis
from schemas.events import BaseJobEvent

class RedisEventEmitter:
    """
    Dedicated Redis Pub/Sub emitter for the Python AI Engine.
    Publishes strongly-typed events to specific channels: `job.{jobId}.{type}`
    """
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url)

    async def emit(self, event: BaseJobEvent):
        """
        Publishes the Pydantic event object to Redis.
        """
        # Event Type Routing: job.123.progress, job.123.completed, etc.
        channel = f"job.{event.jobId}.{event.type}"
        
        # We use Pydantic's built-in JSON serializer
        payload = event.model_dump_json()
        
        try:
            await self.redis.publish(channel, payload)
            print(f"[Redis Emit] {channel} -> {payload}")
        except Exception as e:
            print(f"[Redis Emit Error] Failed to publish to {channel}: {str(e)}")

    async def close(self):
        await self.redis.aclose()
