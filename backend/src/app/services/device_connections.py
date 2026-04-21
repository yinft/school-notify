from collections.abc import Iterable

from fastapi import WebSocket


class DeviceConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, *, device_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[device_id] = websocket

    def disconnect(self, *, device_id: str) -> None:
        self._connections.pop(device_id, None)

    async def send_notifications(self, *, deliveries: Iterable[dict[str, object]]) -> None:
        for delivery in deliveries:
            device_id = str(delivery["device_id"])
            websocket = self._connections.get(device_id)
            if websocket is None:
                continue

            await websocket.send_json(
                {
                    "event": "notification_created",
                    "device_id": device_id,
                    "payload": delivery["payload"],
                }
            )


device_connections = DeviceConnectionManager()
