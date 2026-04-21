from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.device_connections import device_connections
from app.services.store import store


router = APIRouter()


@router.websocket("/ws/devices/{device_id}")
async def device_socket(websocket: WebSocket, device_id: str) -> None:
    await device_connections.connect(device_id=device_id, websocket=websocket)
    await websocket.send_json(
        {
            "event": "connected",
            "device_id": device_id,
            "status": "placeholder",
        }
    )

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            notification_id = message.get("notification_id")
            if event and notification_id:
                store.register_receipt(device_id=device_id, notification_id=notification_id, event=event)
    except WebSocketDisconnect:
        device_connections.disconnect(device_id=device_id)
