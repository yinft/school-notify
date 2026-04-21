from datetime import UTC, datetime
from secrets import randbelow

from app.schemas.binding import BindingCodeResponse, BindingResponse
from app.schemas.device import DeviceResponse
from app.schemas.notification import NotificationCreateResponse, NotificationDeliveryRecord, NotificationRecord
from app.settings import settings


class DeviceNotFoundError(Exception):
    pass


class BindingCodeNotFoundError(Exception):
    pass


class DeviceNotBoundError(Exception):
    pass


class DeviceOfflineError(Exception):
    pass


class InMemoryStore:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.devices: dict[str, DeviceResponse] = {}
        self.binding_codes: dict[str, BindingCodeResponse] = {}
        self.bindings_by_user: dict[str, set[str]] = {}
        self.delivery_receipts: dict[str, dict[str, dict[str, bool]]] = {}
        self.notification_counter = 0
        self.notification_records: list[dict[str, object]] = []

    def register_device(
        self,
        *,
        device_id: str,
        device_name: str,
        client_version: str,
    ) -> DeviceResponse:
        device = DeviceResponse(
            device_id=device_id,
            device_name=device_name,
            client_version=client_version,
            status="online",
            last_seen_at=self._now(),
        )
        self.devices[device_id] = device
        return device

    def list_devices(self) -> list[DeviceResponse]:
        return list(self.devices.values())

    def create_binding_code(self, *, device_id: str) -> BindingCodeResponse:
        self._require_device(device_id)
        binding_code = BindingCodeResponse(
            device_id=device_id,
            code=f"{randbelow(1_000_000):06d}",
            expires_in_seconds=settings.bind_code_expires_seconds,
        )
        self.binding_codes[device_id] = binding_code
        return binding_code

    def heartbeat_device(self, *, device_id: str) -> DeviceResponse:
        device = self._require_device(device_id)
        refreshed = device.model_copy(
            update={
                "status": "online",
                "last_seen_at": self._now(),
            }
        )
        self.devices[device_id] = refreshed
        return refreshed

    def bind_user_to_device(self, *, user_id: str, code: str) -> BindingResponse:
        binding_code = self._require_binding_code(code)
        self.bindings_by_user.setdefault(user_id, set()).add(binding_code.device_id)
        return BindingResponse(user_id=user_id, device_id=binding_code.device_id)

    def list_devices_for_user(self, *, user_id: str) -> list[DeviceResponse]:
        device_ids = self.bindings_by_user.get(user_id, set())
        return [self.devices[device_id] for device_id in device_ids if device_id in self.devices]

    def create_notification(
        self,
        *,
        sender_user_id: str,
        title: str,
        content: str,
        level: str,
        device_ids: list[str],
    ) -> tuple[NotificationCreateResponse, list[dict[str, object]]]:
        bound_device_ids = self.bindings_by_user.get(sender_user_id, set())
        self.notification_counter += 1
        notification_id = f"notification-{self.notification_counter}"
        for device_id in device_ids:
            device = self._require_device(device_id)
            if device_id not in bound_device_ids:
                raise DeviceNotBoundError(device_id)
            if device.status != "online":
                raise DeviceOfflineError(device_id)

            self.delivery_receipts.setdefault(device_id, {})[notification_id] = {
                "received": False,
                "displayed": False,
                "spoken": False,
            }

        self.notification_records.append(
            {
                "notification_id": notification_id,
                "sender_user_id": sender_user_id,
                "title": title,
                "content": content,
                "level": level,
                "target_count": len(device_ids),
                "device_ids": list(device_ids),
            }
        )

        return NotificationCreateResponse(status="accepted", target_count=len(device_ids)), [
            {
                "device_id": device_id,
                "payload": {
                    "notification_id": notification_id,
                    "title": title,
                    "content": content,
                    "level": level,
                },
            }
            for device_id in device_ids
        ]

    def set_device_status(self, *, device_id: str, status: str) -> DeviceResponse:
        device = self._require_device(device_id)
        updated = device.model_copy(update={"status": status})
        self.devices[device_id] = updated
        return updated

    def register_receipt(self, *, device_id: str, notification_id: str, event: str) -> None:
        receipt = self.delivery_receipts.setdefault(device_id, {}).setdefault(
            notification_id,
            {"received": False, "displayed": False, "spoken": False},
        )
        if event == "receipt_received":
            receipt["received"] = True
        if event == "receipt_displayed":
            receipt["displayed"] = True
        if event == "receipt_spoken":
            receipt["spoken"] = True

    def list_notifications_for_user(self, *, sender_user_id: str) -> list[NotificationRecord]:
        items: list[NotificationRecord] = []
        for record in self.notification_records:
            if record["sender_user_id"] != sender_user_id:
                continue

            device_ids = record["device_ids"]
            deliveries = [
                NotificationDeliveryRecord(
                    device_id=device_id,
                    received=self.delivery_receipts.get(device_id, {}).get(record["notification_id"], {}).get("received", False),
                    displayed=self.delivery_receipts.get(device_id, {}).get(record["notification_id"], {}).get("displayed", False),
                    spoken=self.delivery_receipts.get(device_id, {}).get(record["notification_id"], {}).get("spoken", False),
                )
                for device_id in device_ids
            ]
            items.append(
                NotificationRecord(
                    notification_id=record["notification_id"],
                    sender_user_id=record["sender_user_id"],
                    title=record["title"],
                    content=record["content"],
                    level=record["level"],
                    target_count=record["target_count"],
                    deliveries=deliveries,
                )
            )

        return list(reversed(items))

    def _require_device(self, device_id: str) -> DeviceResponse:
        device = self.devices.get(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)
        return device

    def _require_binding_code(self, code: str) -> BindingCodeResponse:
        for binding_code in self.binding_codes.values():
            if binding_code.code == code:
                return binding_code
        raise BindingCodeNotFoundError(code)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)


store = InMemoryStore()
