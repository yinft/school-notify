from datetime import UTC, datetime, timedelta
from secrets import randbelow

from sqlalchemy import delete, select

from app.core.db import SessionLocal
from app.models import AuthSession as AuthSessionModel, ClientVersion, Device as DeviceModel
from app.models import DeviceBindCode, Notification as NotificationModel, NotificationDelivery, User as UserModel, UserDevice
from app.schemas.binding import BindingCodeResponse, BindingResponse
from app.schemas.device import DeviceResponse, DeviceUpdateInfo, HeartbeatResponse
from app.schemas.notification import NotificationCreateResponse, NotificationDeliveryRecord, NotificationRecord
from app.services.redis_service import redis_service
from app.services.wechat_auth import build_device_token
from app.core.settings import settings


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
        if not settings.database_url.startswith("sqlite:///"):
            raise RuntimeError("Refusing to reset non-SQLite database")

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
                return self._to_device_response(existing, include_token=True)

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
            return self._to_device_response(device, include_token=True)

    def list_devices(self) -> list[DeviceResponse]:
        with SessionLocal() as session:
            devices = session.execute(select(DeviceModel)).scalars().all()
            return [self._device_response_with_online_status(device) for device in devices]

    def create_binding_code(self, *, device_id: str) -> BindingCodeResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            existing = session.execute(select(DeviceBindCode).where(DeviceBindCode.device_id == device_id)).scalar_one_or_none()
            if existing is not None:
                redis_service.consume_bind_code(existing.code)

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

    def get_device_by_binding_code(self, *, code: str) -> DeviceResponse:
        with SessionLocal() as session:
            device_id = self._get_valid_bind_device_id(session, code=code, consume_redis=False)
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise BindingCodeNotFoundError(code)
            return self._to_device_response(device)

    def heartbeat_device(self, *, device_id: str) -> HeartbeatResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            device.status = "online"
            device.last_seen_at = self._now()
            session.commit()
            session.refresh(device)
            redis_service.set_device_online(device_id)
            update_info = self._build_update_info(session, device.client_version)
            return HeartbeatResponse(
                device_id=device.device_id,
                device_name=device.device_name,
                location_label=device.location_label,
                client_version=device.client_version,
                status=device.status,
                last_seen_at=device.last_seen_at,
                device_token=build_device_token(device.device_id),
                update=update_info,
            )

    def bind_user_to_device(
        self,
        *,
        user_id: str,
        code: str,
        device_name: str | None = None,
        location_label: str | None = None,
    ) -> BindingResponse:
        with SessionLocal() as session:
            device_id = self._get_valid_bind_device_id(session, code=code, consume_redis=True)

            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise BindingCodeNotFoundError(code)

            if device_name is not None and device_name.strip():
                device.device_name = device_name.strip()
            if location_label is not None:
                device.location_label = location_label.strip()

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
            return [self._device_response_with_online_status(device) for device in devices]

    def unbind_user_from_device(self, *, user_id: str, device_id: str) -> BindingResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            binding = session.execute(
                select(UserDevice).where(UserDevice.user_id == user_id, UserDevice.device_id == device_id)
            ).scalar_one_or_none()
            if binding is None:
                raise DeviceNotBoundError(device_id)

            session.delete(binding)
            session.commit()

            return BindingResponse(user_id=user_id, device_id=device_id)

    def update_bound_device(
        self,
        *,
        user_id: str,
        device_id: str,
        device_name: str | None = None,
        location_label: str | None = None,
    ) -> DeviceResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)

            binding = session.execute(
                select(UserDevice).where(UserDevice.user_id == user_id, UserDevice.device_id == device_id)
            ).scalar_one_or_none()
            if binding is None:
                raise DeviceNotBoundError(device_id)

            if device_name is not None and device_name.strip():
                device.device_name = device_name.strip()
            if location_label is not None:
                device.location_label = location_label.strip()

            session.commit()
            session.refresh(device)
            return self._to_device_response(device)

    def create_notification(
        self,
        *,
        sender_user_id: str,
        title: str,
        content: str,
        level: str,
        device_ids: list[str],
        duration_seconds: int | None = None,
        tts_enabled: bool = True,
        tts_repeat_count: int | None = None,
    ) -> tuple[NotificationCreateResponse, list[dict[str, object]]]:
        with SessionLocal() as session:
            bound_device_ids = set(
                session.execute(select(UserDevice.device_id).where(UserDevice.user_id == sender_user_id)).scalars().all()
            )

            unique_device_ids = list(dict.fromkeys(device_ids))
            if len(unique_device_ids) != len(device_ids):
                raise ValueError("duplicate device ids")

            for device_id in unique_device_ids:
                device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
                if device is None:
                    raise DeviceNotFoundError(device_id)
                if device_id not in bound_device_ids:
                    raise DeviceNotBoundError(device_id)
                is_online = redis_service.is_device_online(device_id) if redis_service.is_enabled() else device.status == "online"
                if not is_online:
                    raise DeviceOfflineError(device_id)

            next_id = (session.execute(select(NotificationModel.id).order_by(NotificationModel.id.desc())).scalars().first() or 0) + 1
            notification_id = f"notification-{next_id}"
            notification = NotificationModel(
                notification_id=notification_id,
                sender_user_id=sender_user_id,
                title=title,
                content=content,
                level=level,
                duration_seconds=duration_seconds,
                tts_enabled=tts_enabled,
                tts_repeat_count=tts_repeat_count,
                target_count=len(unique_device_ids),
            )
            session.add(notification)
            session.flush()

            for device_id in unique_device_ids:
                session.add(
                    NotificationDelivery(
                        notification_id=notification_id,
                        device_id=device_id,
                        received=False,
                        displayed=False,
                        spoken=False,
                        failed=False,
                    )
                )

            session.commit()

            payload = {
                "notification_id": notification_id,
                "title": title,
                "content": content,
                "level": level,
            }
            if duration_seconds is not None:
                payload["duration_seconds"] = duration_seconds
            if not tts_enabled:
                payload["tts_enabled"] = tts_enabled
            if tts_repeat_count is not None:
                payload["tts_repeat_count"] = tts_repeat_count

            return NotificationCreateResponse(status="accepted", target_count=len(unique_device_ids)), [
                {
                    "device_id": device_id,
                    "payload": payload,
                }
                for device_id in unique_device_ids
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

    def mark_delivery_failed(self, *, device_id: str, notification_id: str, error_message: str) -> None:
        with SessionLocal() as session:
            delivery = session.execute(
                select(NotificationDelivery).where(
                    NotificationDelivery.device_id == device_id,
                    NotificationDelivery.notification_id == notification_id,
                )
            ).scalar_one_or_none()
            if delivery is None:
                return
            delivery.failed = True
            delivery.error_message = error_message
            session.commit()

    def list_notifications_for_user(
        self,
        *,
        sender_user_id: str,
        limit: int = 20,
        offset: int = 0,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> tuple[list[NotificationRecord], int]:
        with SessionLocal() as session:
            normalized_start_at = self._normalize_filter_datetime(start_at)
            normalized_end_at = self._normalize_filter_datetime(end_at)
            notifications = session.execute(
                select(NotificationModel)
                .where(NotificationModel.sender_user_id == sender_user_id)
                .order_by(NotificationModel.id.desc())
            ).scalars().all()
            filtered_notifications = [
                notification
                for notification in notifications
                if self._matches_notification_range(
                    notification.created_at,
                    start_at=normalized_start_at,
                    end_at=normalized_end_at,
                )
            ]
            total_count = len(filtered_notifications)
            notifications = filtered_notifications[offset : offset + limit]

            items: list[NotificationRecord] = []
            for record in notifications:
                deliveries_db = session.execute(
                    select(NotificationDelivery).where(NotificationDelivery.notification_id == record.notification_id)
                ).scalars().all()
                delivery_device_ids = [delivery.device_id for delivery in deliveries_db]
                devices_by_id = {
                    device.device_id: device
                    for device in session.execute(
                        select(DeviceModel).where(DeviceModel.device_id.in_(delivery_device_ids))
                    ).scalars().all()
                }
                deliveries = [
                    NotificationDeliveryRecord(
                        device_id=delivery.device_id,
                        device_name=devices_by_id[delivery.device_id].device_name if delivery.device_id in devices_by_id else "",
                        location_label=devices_by_id[delivery.device_id].location_label if delivery.device_id in devices_by_id else "",
                        received=delivery.received,
                        displayed=delivery.displayed,
                        spoken=delivery.spoken,
                        failed=delivery.failed,
                        error_message=delivery.error_message,
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
                        duration_seconds=record.duration_seconds,
                        tts_enabled=record.tts_enabled,
                        tts_repeat_count=record.tts_repeat_count,
                        target_count=record.target_count,
                        created_at=record.created_at.isoformat(),
                        deliveries=deliveries,
                    )
                )
            return items, total_count

    def _normalize_filter_datetime(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value

        normalized = value.astimezone(UTC)
        if settings.database_url.startswith("sqlite:///"):
            return normalized.replace(tzinfo=None)
        return normalized

    def _matches_notification_range(self, created_at: datetime, *, start_at: datetime | None, end_at: datetime | None) -> bool:
        normalized_created_at = self._normalize_filter_datetime(created_at)
        if start_at is not None and normalized_created_at < start_at:
            return False
        if end_at is not None and normalized_created_at >= end_at:
            return False
        return True

    def _require_device(self, device_id: str) -> DeviceResponse:
        with SessionLocal() as session:
            device = session.execute(select(DeviceModel).where(DeviceModel.device_id == device_id)).scalar_one_or_none()
            if device is None:
                raise DeviceNotFoundError(device_id)
            return self._to_device_response(device)

    def _get_valid_bind_device_id(self, session, *, code: str, consume_redis: bool) -> str:
        device_id = redis_service.get_bind_device_id(code)
        if device_id is not None:
            binding_code = session.execute(select(DeviceBindCode).where(DeviceBindCode.code == code)).scalar_one_or_none()
            if binding_code is not None and self._is_binding_code_expired(binding_code):
                redis_service.consume_bind_code(code)
                session.execute(delete(DeviceBindCode).where(DeviceBindCode.code == code))
                session.commit()
                raise BindingCodeNotFoundError(code)
            if consume_redis:
                redis_service.consume_bind_code(code)
            return device_id

        binding_code = session.execute(select(DeviceBindCode).where(DeviceBindCode.code == code)).scalar_one_or_none()
        if binding_code is None:
            raise BindingCodeNotFoundError(code)
        if self._is_binding_code_expired(binding_code):
            session.execute(delete(DeviceBindCode).where(DeviceBindCode.code == code))
            session.commit()
            raise BindingCodeNotFoundError(code)
        return binding_code.device_id

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
    def _to_device_response(device: DeviceModel, *, include_token: bool = False) -> DeviceResponse:
        return DeviceResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            location_label=device.location_label,
            client_version=device.client_version,
            status=device.status,
            last_seen_at=device.last_seen_at,
            device_token=build_device_token(device.device_id) if include_token else "",
        )

    def _device_response_with_online_status(self, device: DeviceModel) -> DeviceResponse:
        if redis_service.is_enabled() and redis_service.is_device_online(device.device_id):
            status = "online"
            last_seen_str = redis_service.get_device_last_seen(device.device_id)
            last_seen = datetime.fromisoformat(last_seen_str) if last_seen_str else device.last_seen_at
        else:
            status = device.status if not redis_service.is_enabled() else "offline"
            last_seen = device.last_seen_at
        return DeviceResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            location_label=device.location_label,
            client_version=device.client_version,
            status=status,
            last_seen_at=last_seen,
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now()

    @staticmethod
    def _is_newer_version(current: str, latest: str) -> bool:
        try:
            cur = tuple(int(p) for p in current.split("."))
            lat = tuple(int(p) for p in latest.split("."))
            return lat > cur
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def _build_update_info(session, client_version: str) -> DeviceUpdateInfo | None:
        recommended = session.execute(
            select(ClientVersion).where(
                ClientVersion.platform == "windows",
                ClientVersion.is_published.is_(True),
                ClientVersion.is_recommended.is_(True),
            )
        ).scalar_one_or_none()

        if recommended is None:
            return None

        if not InMemoryStore._is_newer_version(client_version, recommended.version):
            return DeviceUpdateInfo(
                available=False,
                current_version=client_version,
            )

        return DeviceUpdateInfo(
            available=True,
            current_version=client_version,
            latest_version=recommended.version,
            download_url=recommended.download_url,
            file_size=recommended.file_size,
        )

    def _is_binding_code_expired(self, binding_code: DeviceBindCode) -> bool:
        created_at = binding_code.created_at
        if created_at.tzinfo is not None:
            created_at = created_at.astimezone().replace(tzinfo=None)
        return created_at + timedelta(seconds=binding_code.expires_in_seconds) < self._now()


store = InMemoryStore()
