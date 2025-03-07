# Dyffi-Bus

**Dyffi-Bus** is a simple asynchronous Pub/Sub system built with FastAPI and an in-memory broker. It allows you to publish messages to topics, subscribe via WebSockets, and optionally log messages to JSON files.

## Features

- **Asynchronous**: Uses FastAPI and asyncio for non-blocking I/O.
- **Pub/Sub**: Publish messages to named topics; any subscribers to that topic receive them in real time.
- **WebSocket Support**: Real-time message delivery to connected clients.
- **Optional File Logging**: Can write published messages to JSON files for persistence.

## How It Works

1. **Broker**: An in-memory broker (`CustomAsyncBroker` or `LocalAsyncBroker`) holds subscriptions and distributes messages to subscribers.
2. **FastAPI**: Exposes two main endpoints:
   - `POST /publish` for publishing messages to a topic (JSON payload).
   - `GET /ws/{topic}` (WebSocket) for subscribing to a topic and receiving messages.
3. **Client Library**: An optional Python client (`DyffiClient`) can simplify publishing (via HTTP) and subscribing (via WebSocket).

### Architecture Overview

```
              [Publisher]        [Publisher]
                   |                  |
                   v                  v
            (POST /publish)    (POST /publish)
               \____________ ___________/
                            |
                       [Dyffi-Bus]
                            |
         [Subscriber] [Subscriber] [Subscriber]
               |           |             |
               v           v             v
         (WebSocket)  (WebSocket)   (WebSocket)
```

## Usage

### 1. Local (Without Docker)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```
3. **Publish Messages** (Example with `curl`):
   ```bash
   curl -X POST -H "Content-Type: application/json"    -d '{"topic": "orders", "payload": {"order_id": 123, "customer": "Alice"}}'    http://127.0.0.1:8000/publish
   ```
4. **Subscribe**:
   - Open a WebSocket connection to `ws://127.0.0.1:8000/ws/{TOPIC_NAME}` (for example, recommending using client lib `DyffiClient`).

### 2. Docker

#### Pull the Image

```bash
docker pull flap1ks/dyffi-bus:latest
```

#### Run a Container

```bash
docker run -d     -p 8000:8000     --name dyffi-bus     flap1ks/dyffi-bus:latest
```

- Access the app at `http://localhost:8000`.
- Publish messages at `http://localhost:8000/publish`.
- Subscribe to `ws://localhost:8000/ws/{topic}`.

#### Optional: Logging to Files

If you want to enable file-based logging, set environment variables when running the container:

- `LOGGING_ENABLED=true` (default is `true`, set to `false` to disable)
- `LOGS_FOLDER=/app/logs` (or any other path)

And map a volume to persist logs on the host:

```bash
docker run -d -p 8000:8000 -e LOGGING_ENABLED=true -e LOGS_FOLDER=/app/logs -v /path/on/host/logs:/app/logs --name dyffi-bus flap1ks/dyffi-bus:latest 
```

This way, your logs will be stored on the host system even if the container is removed.

## Deployment

- **Docker** is the easiest way to deploy. Pull and run the image on your server or cloud instance.
- **Kubernetes**: You can create a simple Deployment/Service YAML that pulls `flap1ks/dyffi-bus:latest` and exposes port 8000.
 
## Example: Using the Python Client

```python
# example_sub.py
from client import DyffiBusClient

def handle_message(message):
    print("Received:", message)

client = DyffiBusClient("http://localhost:8000")
client.subscribe("orders", handle_message, blocking=True)
```

Run:
```bash
python app.py
```

Then in another terminal:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"topic": "orders", "payload": {"order_id": 123}}' http://localhost:8000/publish
```

Your `handle_message` function will print the message immediately.

## Contributing

- Fork the repository, make changes, and create a pull request.
- Feel free to open issues for bug reports or feature requests.

## License

[MIT License](LICENSE) – you’re free to use, modify, and distribute this software, as long as you include the license text.
