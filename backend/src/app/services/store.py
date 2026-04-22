from datetime import UTC, datetime
from secrets import randbelow

from sqlalchemy import delete, select

from app.db import SessionLocal
from app.models import AuthSession as AuthSessionModel, Device as DeviceModel
from app.models import DeviceBindCode, Notification as NotificationModel, NotificationDelivery, User as UserModel, UserDevice
from app.schemas.binding import BindingCodeResponse, BindingResponse
from app.schemas.device import DeviceResponse
from app.schemas.notification import NotificationCreateResponse, NotificationDeliveryRecord, NotificationRecord
from app.services.redis_service import redis_service
from app.services.wechat_auth import build_device_token
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
        pass

    def reset(self) -> None:
        with SessionLocal() as session:
            session.execute(delete(NotificationDelivery))
            session.execute(delete(NotificationModel))
            session.execute(delete(UserDevice))
            session.execute(delete(DeviceBindCode))
            session.execute(delete(DeviceModel))
            session.execute(delete(AuthSessionModel))
            session.execute(delete(UserModel))
            session.commit()

    def register_device(
        self,
        *,
        device_id: str,
        device_name: str,
        client_version: str,
    ) -> DeviceResponse:
        with SessionLocal() as session:
            existing = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if existing:
                existing.device_name = device_name
                existing.client_version = client_version
                existing.status = "online"
                existing.last_seen_at = self._now()
                session.commit()
                session.refresh(existing)
                redis_service.set_device_online(device_id)
                return self._to_device_response(existing)

            device = DeviceModel(
                device_id=device_id,
                device_name=device_name,
                client_version=client_version,
                status="online",
                last_seen_at=self._now(),
            )
            session.add(device)
            session.commit()
            session.refresh(device)
            redis_service.set_device_online(device_id)
            return self._to_device_response(device)

    def list_devices(self) -> list[DeviceResponse]:
        with SessionLocal() as session:
            devices = session.execute(select(DeviceModel)).scalars().all()
            results: list[DeviceResponse] = []
            for device in devices:
                if redis_service.is_device_online(device.device_id):
                    status = "online"
                    last_seen_str = redis_service.get_device_last_seen(device.device_id)
                    last_seen = datetime.fromisoformat(last_seen_str) if last_seen_str else device.last_seen_at
                else:
                    status = device.status
                    last_seen = device.last_seen_at
                results.append(
                    DeviceResponse(
                        device_id=device.device_id,
                        device_name=device.device_name,
                        client_version=device.client_version,
                        status=status,
                        last_seen_at=last_seen,
                    )
                )
            return results

    def create_binding_code(self, *, device_id: str) -> BindingCodeResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            session.execute(delete(DeviceBindCode).where(DeviceBindCode.device_id == device_id))
            binding_code = DeviceBindCode(
                device_id=device_id,
                code=f"{randbelow(1_000_000):06d}",
                expires_in_seconds=settings.bind_code_expires_seconds,
            )
            session.add(binding_code)
            session.commit()
            redis_service.cache_bind_code(
                code=binding_code.code,
                device_id=device_id,
                ttl_seconds=binding_code.expires_in_seconds,
            )
            return BindingCodeResponse(
                device_id=device_id,
                code=binding_code.code,
                expires_in_seconds=binding_code.expires_in_seconds,
            )

    def heartbeat_device(self, *, device_id: str) -> DeviceResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            device.status = "online"
            device.last_seen_at = self._now()
            session.commit()
            session.refresh(device)
            redis_service.set_device_online(device_id)
            return self._to_device_response(device)

    def bind_user_to_device(self, *, user_id: str, code: str) -> BindingResponse:
        with SessionLocal() as session:
            device_id = redis_service.get_bind_device_id(code)

            if device_id is None:
                binding_code = session.execute(select(DeviceBindCode).where(DeviceBindCode.code == code)).scalar_one_or_none()
                if binding_code is None:
                    raise BindingCodeNotFoundError(code)
                device_id = binding_code.device_id
            else:
                redis_service.consume_bind_code(code)

            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise BindingCodeNotFoundError(code)

            session.execute(delete(DeviceBindCode).where(DeviceBindCode.code == code))

            existing = session.execute(
                select(UserDevice).where(UserDevice.user_id == user_id, UserDevice.device_id == device_id)
            ).scalar_one_or_none()
            if existing is None:
                session.add(UserDevice(user_id=user_id, device_id=device_id))

            session.commit()

            return BindingResponse(user_id=user_id, device_id=device_id)

    def list_devices_for_user(self, *, user_id: str) -> list[DeviceResponse]:
        with SessionLocal() as session:
            device_ids = session.execute(select(UserDevice.device_id).where(UserDevice.user_id == user_id)).scalars().all()
            if not device_ids:
                return []
            devices = session.execute(select(DeviceModel).where(DeviceModel.device_id.in_(device_ids))).scalars().all()
            return [self._to_device_response(device) for device in devices]

    def create_notification(
        self,
        *,
        sender_user_id: str,
        title: str,
        content: str,
        level: str,
        device_ids: list[str],
    ) -> tuple[NotificationCreateResponse, list[dict[str, object]]]:
        with SessionLocal() as session:
            bound_device_ids = set(
                session.execute(select(UserDevice.device_id).where(UserDevice.user_id == sender_user_id)).scalars().all()
            )

            for device_id in device_ids:
                device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
                if device is None:
                    raise DeviceNotFoundError(device_id)
                if device_id not in bound_device_ids:
                    raise DeviceNotBoundError(device_id)
                if not redis_service.is_device_online(device_id) and device.status != "online":
                    raise DeviceOfflineError(device_id)

            next_id = (session.execute(select(NotificationModel.id).order_by(NotificationModel.id.desc())).scalars().first() or 0) + 1
            notification_id = f"notification-{next_id}"
            notification = NotificationModel(
                notification_id=notification_id,
                sender_user_id=sender_user_id,
                title=title,
                content=content,
                level=level,
                target_count=len(device_ids),
            )
            session.add(notification)
            session.flush()

            for device_id in device_ids:
                session.add(
                    NotificationDelivery(
                        notification_id=notification_id,
                        device_id=device_id,
                        received=False,
                        displayed=False,
                        spoken=False,
                    )
                )

            session.commit()

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
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)
            device.status = status
            session.commit()
            session.refresh(device)
            if status == "online":
                redis_service.set_device_online(device_id)
            else:
                redis_service.set_device_offline(device_id)
            return self._to_device_response(device)

    def register_receipt(self, *, device_id: str, notification_id: str, event: str) -> None:
        with SessionLocal() as session:
            delivery = session.execute(
                select(NotificationDelivery).where(
                    NotificationDelivery.device_id == device_id,
                    NotificationDelivery.notification_id == notification_id,
                )
            ).scalar_one_or_none()

            if delivery is not None:
                if event == "receipt_received":
                    delivery.received = True
                if event == "receipt_displayed":
                    delivery.displayed = True
                if event == "receipt_spoken":
                    delivery.spoken = True
                session.commit()

    def list_notifications_for_user(self, *, sender_user_id: str, limit: int = 20, offset: int = 0) -> tuple[list[NotificationRecord], int]:
        with SessionLocal() as session:
            total = session.execute(
                select(NotificationModel.id).where(NotificationModel.sender_user_id == sender_user_id)
            ).scalars().all()
            total_count = len(total)

            notifications = session.execute(
                select(NotificationModel)
                .where(NotificationModel.sender_user_id == sender_user_id)
                .order_by(NotificationModel.id.desc())
                .offset(offset)
                .limit(limit)
            ).scalars().all()

            items: list[NotificationRecord] = []
            for record in notifications:
                deliveries_db = session.execute(
                    select(NotificationDelivery).where(NotificationDelivery.notification_id == record.notification_id)
                ).scalars().all()
                deliveries = [
                    NotificationDeliveryRecord(
                        device_id=delivery.device_id,
                        received=delivery.received,
                        displayed=delivery.displayed,
                        spoken=delivery.spoken,
                    )
                    for delivery in deliveries_db
                ]
                items.append(
                    NotificationRecord(
                        notification_id=record.notification_id,
                        sender_user_id=record.sender_user_id,
                        title=record.title,
                        content=record.content,
                        level=record.level,
                        target_count=record.target_count,
                        deliveries=deliveries,
                    )
                )
            return items, total_count

    def _require_device(self, device_id: str) -> DeviceResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)
            return self._to_device_response(device)

    def _require_binding_code(self, code: str) -> BindingCodeResponse:
        with SessionLocal() as session:
            binding_code = session.execute(select(DeviceBindCode).where(DeviceBindCode.code == code)).scalar_one_or_none()
            if binding_code is None:
                raise BindingCodeNotFoundError(code)
            return BindingCodeResponse(
                device_id=binding_code.device_id,
                code=binding_code.code,
                expires_in_seconds=binding_code.expires_in_seconds,
            )

    @staticmethod
    def _to_device_response(device: DeviceModel) -> DeviceResponse:
        return DeviceResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            client_version=device.client_version,
            status=device.status,
            last_seen_at=device.last_seen_at,
            device_token=build_device_token(device.device_id),
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)


store = InMemoryStore()
