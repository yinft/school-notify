from app.services.redis_service import RedisService


class _FakePipeline:
    def __init__(self) -> None:
        self.ops: list[tuple] = []

    def setex(self, key: str, ttl: int, value: str):
        self.ops.append(("setex", key, ttl, value))
        return self

    def set(self, key: str, value: str):
        self.ops.append(("set", key, value))
        return self

    def execute(self):
        return True


class _FakeClient:
    def __init__(self) -> None:
        self.pipeline_obj = _FakePipeline()

    def pipeline(self):
        return self.pipeline_obj


def test_set_device_online_sets_ttl_for_last_seen_key() -> None:
    service = RedisService()
    fake_client = _FakeClient()
    service._client = fake_client

    service.set_device_online("device-001", ttl=45)

    online_key = service._device_online_key("device-001")
    last_seen_key = service._device_last_seen_key("device-001")
    assert ("setex", online_key, 45, "1") in fake_client.pipeline_obj.ops
    assert any(op[0] == "setex" and op[1] == last_seen_key and op[2] == 90 for op in fake_client.pipeline_obj.ops)
