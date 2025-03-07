import asyncio
import json
from collections import defaultdict

class CustomAsyncBroker:
    """
    A local, in-memory broker that mimics basic Redis pub/sub behavior.
    Useful for development or testing without requiring a real Redis instance.
    """
    _instance = None  # Singleton instance

    def __init__(self, decode_responses=True):
        self.decode_responses = decode_responses
        self._subscribers = {}  # {channel: [CustomAsyncPubSub, ...]}
        # Store messages if no subscriber is around at publish-time
        self._pending_messages = defaultdict(list)  # {channel: [message, ...]}
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls, decode_responses=True):
        if cls._instance is None:
            cls._instance = cls(decode_responses)
        return cls._instance

    async def publish(self, channel, message):
        async with self._lock:
            # Check if we currently have subscribers for this channel
            if channel in self._subscribers and self._subscribers[channel]:
                # Deliver to all existing subscribers
                for pubsub in list(self._subscribers[channel]):
                    await pubsub.queue.put({
                        "type": "message",
                        "data": message,
                        "channel": channel
                    })
            else:
                # No subscribers yet, store in pending
                self._pending_messages[channel].append(message)

    def pubsub(self):
        return CustomAsyncPubSub(self)

    async def close(self):
        # Nothing to clean up in this in-memory version
        pass

    async def add_subscriber(self, channel, pubsub):
        async with self._lock:
            if channel not in self._subscribers:
                self._subscribers[channel] = []
            self._subscribers[channel].append(pubsub)

            # Отправляем все ранее накопленные сообщения новому подписчику
            if channel in self._pending_messages:
                for msg in self._pending_messages[channel]:
                    await pubsub.queue.put({
                        "type": "message",
                        "data": msg,
                        "channel": channel
                    })
                # ВАЖНО: не очищаем список, чтобы сообщения
                #        были доступны для будущих подписчиков,
                #        если это требуется вашей логикой.
                #
                # Если нужно, чтобы только первый подписчик получил историю,
                # можно раскомментировать строку ниже:
                #
                # self._pending_messages[channel].clear()

    async def remove_subscriber(self, channel, pubsub):
        async with self._lock:
            if channel in self._subscribers and pubsub in self._subscribers[channel]:
                self._subscribers[channel].remove(pubsub)


class CustomAsyncPubSub:
    def __init__(self, broker: CustomAsyncBroker):
        self.broker = broker
        self.queue = asyncio.Queue()
        self.channels = set()

    async def subscribe(self, channel: str):
        self.channels.add(channel)
        await self.broker.add_subscriber(channel, self)

    async def unsubscribe(self, channel: str):
        self.channels.discard(channel)
        await self.broker.remove_subscriber(channel, self)

    async def get_message(self, ignore_subscribe_messages=False, timeout=1.0):
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
