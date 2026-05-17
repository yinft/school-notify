import base64
import hashlib
import hmac
import json
import time


QINIU_UPLOAD_URL = "https://upload.qiniup.com"


class QiniuConfigMissingError(Exception):
    pass


def _urlsafe_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def build_avatar_key(*, user_id: str) -> str:
    return f"avatars/{user_id}/{int(time.time() * 1000)}.png"


def build_public_url(*, domain: str, key: str) -> str:
    normalized_domain = domain.strip().rstrip("/")
    if not normalized_domain.startswith(("http://", "https://")):
        normalized_domain = f"https://{normalized_domain}"
    return f"{normalized_domain}/{key}"


def build_upload_token(*, access_key: str, secret_key: str, bucket: str, key: str, expires_seconds: int = 300) -> str:
    if not access_key or not secret_key or not bucket:
        raise QiniuConfigMissingError

    policy = {
        "scope": f"{bucket}:{key}",
        "deadline": int(time.time()) + expires_seconds,
    }
    encoded_policy = _urlsafe_base64(json.dumps(policy, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret_key.encode("utf-8"), encoded_policy.encode("ascii"), hashlib.sha1).digest()
    encoded_signature = _urlsafe_base64(signature)
    return f"{access_key}:{encoded_signature}:{encoded_policy}"
