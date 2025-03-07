import asyncio
from custom_async_broker import CustomAsyncBroker


class TopicManager:
    _managers = {}

    def __init__(self, topic):
        self.topic = topic
        self.websockets = set()
        self.task = None
        self.broker = CustomAsyncBroker.get_instance()

    async def start(self):
        if self.task is None:
            self.task = asyncio.create_task(self._listener())

    async def _listener(self):
        pubsub = self.broker.pubsub()
        await pubsub.subscribe(self.topic)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("data"):
                    data = message["data"]
                    for ws in list(self.websockets):
                        try:
                            await ws.send_json(data)
                        except Exception as e:
                            print(f"Error while sending message: {e}")
                            self.websockets.remove(ws)
        except asyncio.CancelledError:
            print(f"[TopicManager] Background task '{self.topic}' cancelled")
        finally:
            await pubsub.unsubscribe(self.topic)
            print(f"[TopicManager] Unsubscribed from topic '{self.topic}'")

    def add_ws(self, ws):
        self.websockets.add(ws)
        print(f"[TopicManager] WebSocket added to topic '{self.topic}'")

    def remove_ws(self, ws):
        self.websockets.discard(ws)
        print(f"[TopicManager] WebSocket removed from topic '{self.topic}'")
        if not self.websockets and self.task:
            self.task.cancel()
            self.task = None
            TopicManager._managers.pop(self.topic, None)

    @classmethod
    async def get_manager(cls, topic):
        if topic not in cls._managers:
            manager = TopicManager(topic)
            cls._managers[topic] = manager
            await manager.start()
        return cls._managers[topic]
