import hashlib
import hmac

import httpx

from app.core.settings import settings


class WeChatLoginError(Exception):
    pass


def exchange_code_for_session(code: str) -> dict[str, str]:
    response = httpx.get(
        settings.wechat_code2session_url,
        params={
            "appid": settings.wechat_app_id,
            "secret": settings.wechat_app_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    openid = payload.get("openid")
    if not openid:
        raise WeChatLoginError("missing openid")
    return payload


def build_session_token(openid: str) -> str:
    signature = hmac.new(
        settings.session_signing_secret.encode("utf-8"),
        openid.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"wechat-session:{openid}:{signature}"


def parse_session_token(token: str) -> str:
    prefix, separator, remainder = token.partition(":")
    if prefix == "device-token":
        return _parse_device_token(remainder)
    if prefix != "wechat-session" or not separator:
        raise WeChatLoginError("invalid session token")

    openid, separator, signature = remainder.partition(":")
    if not openid or not separator or not signature:
        raise WeChatLoginError("invalid session token")

    expected_signature = build_session_token(openid).rsplit(":", 1)[-1]
    if not hmac.compare_digest(signature, expected_signature):
        raise WeChatLoginError("invalid session token")

    return openid


def build_device_token(device_id: str) -> str:
    signature = hmac.new(
        settings.session_signing_secret.encode("utf-8"),
        f"device:{device_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"device-token:{device_id}:{signature}"


def _parse_device_token(remainder: str) -> str:
    device_id, separator, signature = remainder.partition(":")
    if not device_id or not separator or not signature:
        raise WeChatLoginError("invalid device token")

    expected = build_device_token(device_id).rsplit(":", 1)[-1]
    if not hmac.compare_digest(signature, expected):
        raise WeChatLoginError("invalid device token")

    return device_id
