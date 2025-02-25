import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from broker import DyffiBroker
from consumer import DyffiConsumer
from custom_async_broker import CustomAsyncBroker
from pydantic import BaseModel

app = FastAPI()
broker = DyffiBroker()


class PublishMessage(BaseModel):
    topic: str
    payload: dict


@app.post("/publish")
async def publish_message(message: PublishMessage):
    message_id = await broker.publish(message.topic, message.payload)
    return {"message_id": message_id}


@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    await websocket.accept()

    local_broker = CustomAsyncBroker.get_instance()

    async def ws_handler(data):
        # The handler is simply "send to WebSocket"
        await websocket.send_json(data)

    consumer = DyffiConsumer(topic, ws_handler, broker=local_broker)
    consumer_task = asyncio.create_task(consumer.listen())

    try:
        await consumer_task
    except WebSocketDisconnect:
        print(f"WebSocket for topic '{topic}' closed by client.")
        consumer_task.cancel()
