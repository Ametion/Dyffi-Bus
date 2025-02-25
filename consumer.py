import asyncio
import json
from custom_async_broker import CustomAsyncBroker


class DyffiConsumer:
    def __init__(self, topic, handler, broker=None):
        self.broker = broker or CustomAsyncBroker.get_instance(decode_responses=True)
        self.topic = topic
        self.handler = handler

    async def listen(self):
        pubsub = self.broker.pubsub()
        await pubsub.subscribe(self.topic)
        print(f"[Consumer] Subscribed to topic '{self.topic}'")

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("data"):
                    data = json.loads(message["data"])
                    # Since handler is async, just awaiting it directly
                    await self.handler(data)
        finally:
            # Make sure to unsubscribe so we don't leak
            await pubsub.unsubscribe(self.topic)
            print(f"[Consumer] Unsubscribed from topic '{self.topic}'")
