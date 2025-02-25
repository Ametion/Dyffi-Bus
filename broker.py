# broker.py
import os
import uuid
import json
import asyncio
import aiofiles
from pathlib import Path

from custom_async_broker import CustomAsyncBroker

LOGGING_ENABLED = os.getenv("LOGGING_ENABLED", "true").lower() == "true"
LOGS_FOLDER = os.getenv("LOGS_FOLDER", "logs")  # default to 'logs' in-container


class DyffiBroker:
    def __init__(self):
        self.broker = CustomAsyncBroker.get_instance(decode_responses=True)
        self._file_lock = asyncio.Lock()

    async def publish(self, topic, payload):
        message_id = str(uuid.uuid4())
        message = {"id": message_id, "topic": topic, "payload": payload}

        if LOGGING_ENABLED:
            await self.save_to_file(topic, message)

        await self.broker.publish(topic, json.dumps(message))
        print(f"[Broker] Message {message_id} sent to topic '{topic}'")
        return message_id

    async def save_to_file(self, topic, message):
        Path(LOGS_FOLDER).mkdir(parents=True, exist_ok=True)
        file_path = Path(LOGS_FOLDER) / f"{topic}.json"

        async with self._file_lock:
            existing_messages = []
            if file_path.exists():
                async with aiofiles.open(file_path, "r") as f:
                    content = await f.read()
                    if content.strip():
                        existing_messages = json.loads(content)

            existing_messages.append(message)

            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(existing_messages, ensure_ascii=False))
