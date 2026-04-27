from collections.abc import Iterable

from fastapi import WebSocket

from app.services.redis_service import redis_service


class DeviceConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, *, device_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[device_id] = websocket

    def disconnect(self, *, device_id: str) -> None:
        self._connections.pop(device_id, None)

    async def send_notifications(self, *, deliveries: Iterable[dict[str, object]]) -> list[str]:
        failed_device_ids: list[str] = []
        for delivery in deliveries:
            device_id = str(delivery["device_id"])
            websocket = self._connections.get(device_id)
            if websocket is None:
                failed_device_ids.append(device_id)
                continue

            try:
                await websocket.send_json(
                    {
                        "event": "notification_created",
                        "device_id": device_id,
                        "payload": delivery["payload"],
                    }
                )
            except Exception:
                self.mark_offline(device_id=device_id)
                failed_device_ids.append(device_id)
        return failed_device_ids

    def mark_offline(self, *, device_id: str) -> None:
        self.disconnect(device_id=device_id)
        redis_service.set_device_offline(device_id)
        from app.services.store import DeviceNotFoundError, store

        try:
            store.set_device_status(device_id=device_id, status="offline")
        except DeviceNotFoundError:
            return


device_connections = DeviceConnectionManager()
