from __future__ import annotations

from redis import Redis
from redis.exceptions import RedisError

from app.core.settings import settings


class RedisService:
    def __init__(self) -> None:
        self._client: Redis | None = None
        if settings.redis_url:
            self._client = Redis.from_url(settings.redis_url, password=settings.redis_password or None, decode_responses=True)

    def cache_bind_code(self, *, code: str, device_id: str, ttl_seconds: int) -> None:
        if not self._client:
            return
        try:
            self._client.setex(self._bind_code_key(code), ttl_seconds, device_id)
        except RedisError:
            return

    def get_bind_device_id(self, code: str) -> str | None:
        if not self._client:
            return None
        try:
            value = self._client.get(self._bind_code_key(code))
            return value if isinstance(value, str) and value else None
        except RedisError:
            return None

    def consume_bind_code(self, code: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(self._bind_code_key(code))
        except RedisError:
            return

    def cache_auth_session(self, *, session_token: str, user_id: str, ttl_seconds: int) -> None:
        if not self._client:
            return
        try:
            self._client.setex(self._auth_session_key(session_token), ttl_seconds, user_id)
        except RedisError:
            return

    def get_cached_auth_user(self, session_token: str) -> str | None:
        if not self._client:
            return None
        try:
            value = self._client.get(self._auth_session_key(session_token))
            return value if isinstance(value, str) and value else None
        except RedisError:
            return None

    def revoke_cached_auth_session(self, session_token: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(self._auth_session_key(session_token))
        except RedisError:
            return

    def set_device_online(self, device_id: str, ttl: int = 0) -> None:
        if ttl <= 0:
            ttl = settings.device_online_ttl_seconds
        if not self._client:
            return
        try:
            from datetime import UTC, datetime

            now = datetime.now(UTC).isoformat()
            last_seen_ttl = ttl * 2
            pipe = self._client.pipeline()
            pipe.setex(self._device_online_key(device_id), ttl, "1")
            pipe.setex(self._device_last_seen_key(device_id), last_seen_ttl, now)
            pipe.execute()
        except RedisError:
            return

    def is_device_online(self, device_id: str) -> bool:
        if not self._client:
            return False
        try:
            return bool(self._client.exists(self._device_online_key(device_id)))
        except RedisError:
            return False

    def get_device_last_seen(self, device_id: str) -> str | None:
        if not self._client:
            return None
        try:
            value = self._client.get(self._device_last_seen_key(device_id))
            return value if isinstance(value, str) and value else None
        except RedisError:
            return None

    def set_device_offline(self, device_id: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(self._device_online_key(device_id))
        except RedisError:
            return

    def _bind_code_key(self, code: str) -> str:
        return f"{settings.redis_key_prefix}:bind-code:{code}"

    def _auth_session_key(self, session_token: str) -> str:
        return f"{settings.redis_key_prefix}:auth-session:{session_token}"

    def _device_online_key(self, device_id: str) -> str:
        return f"{settings.redis_key_prefix}:device-online:{device_id}"

    def _device_last_seen_key(self, device_id: str) -> str:
        return f"{settings.redis_key_prefix}:device-last-seen:{device_id}"


redis_service = RedisService()
