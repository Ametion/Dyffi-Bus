# Dyffi-Bus

**Dyffi-Bus**  is a simple asynchronous pub/sub system built with FastAPI and an in-memory broker. It lets you publish messages to different topics, and multiple consumers can subscribe to receive those messages in real time. Everything is asynchronous, and you can switch to an external broker (like Redis) if your project grows. It supports WebSockets for browser or Python subscribers, and optionally logs all published messages to JSON files.

## Features

- **Asynchronous**: Uses FastAPI and asyncio for non-blocking I/O.
- **Pub/Sub**: Publish messages to named topics; any subscribers to that topic receive them in real time.
- **WebSocket Support**: Real-time message delivery to connected clients.
- **Optional File Logging**: Can write published messages to JSON files for persistence.
- **Topic Manager**: A centralized Topic Manager that handles all subscribers on a single topic


## How It Works

1. A broker handles subscribing, unsubscribing, and sending messages to clients.
2. When you publish a message, it’s stored until a subscriber is ready.
3. You publish by sending a POST request to /publish with a topic and payload.
4. You receive messages by connecting to /ws/<topic> over WebSockets.
5. This setup simplifies real-time communication between producers and consumers.

### Architecture Overview

```
              [Publisher]        [Publisher]
                   |                  |
                   v                  v
            (POST /publish)    (POST /publish)
               \____________ ___________/
                            |
                      [Topic Manager]
                            |
         [Subscriber] [Subscriber] [Subscriber]
               |           |             |
               v           v             v
         (WebSocket)  (WebSocket)   (WebSocket)
```

## Usage

### 1. Docker

#### Pull the Image

```bash
docker pull flap1ks/dyffi-bus:latest
```

#### Run a Container

```bash
docker run -d -p 8000:8000 --name dyffi-bus flap1ks/dyffi-bus:latest
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

### 2. Local (Without Docker)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/Ametion/Dyffi-Bus.git
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```
4. **Publish Messages** (Example with `curl`):
   ```bash
   curl -X POST -H "Content-Type: application/json"    -d '{"topic": "orders", "payload": {"order_id": 123, "customer": "Alice"}}'    http://127.0.0.1:8000/publish
   ```
5. **Subscribe**:
   - Open a WebSocket connection to `ws://127.0.0.1:8000/ws/{TOPIC_NAME}` (for example, recommending using client lib `DyffiClient`).

## Deployment

- **Docker** is the easiest way to deploy. Pull and run the image on your server or cloud instance.
- **Kubernetes**: You can create a simple Deployment/Service YAML that pulls `flap1ks/dyffi-bus:latest` and exposes port 8000.
 
## Example: Using the Python Client

### Installation

```bash
pip install dyffi_bus_client
```

### Usage (Subscribing to Topic)

```python
from client import DyffiBusClient

def handle_message(message):
    print("Received:", message)

client = DyffiBusClient("http://localhost:8000")
client.subscribe("orders", handle_message, blocking=True)
```

Run:
```bash
python subscription.py
```

### Usage (Publishing to Topic)

```python
from client import DyffiBusClient

client = DyffiBusClient("http://localhost:8000")

message_id = client.publish("orders", {"order_id": 123, "customer": "Alice"})
print("Sent message with ID:", message_id)
```

Run:
```bash
python publishing.py
```

### Now you can see the message published in the terminal where you ran the subscription script.

## Contributing

- Fork the repository, make changes, and create a pull request.
- Feel free to open issues for bug reports or feature requests.

## License

[MIT License](LICENSE) – you’re free to use, modify, and distribute this software, as long as you include the license text.
