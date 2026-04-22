from app.services.wechat_auth import WeChatLoginError, build_session_token, parse_session_token


def test_session_token_round_trip(monkeypatch) -> None:
    monkeypatch.setattr("app.services.wechat_auth.settings.session_signing_secret", "test-secret")

    token = build_session_token("wx-openid-001")

    assert parse_session_token(token) == "wx-openid-001"


def test_parse_session_token_rejects_tampered_signature(monkeypatch) -> None:
    monkeypatch.setattr("app.services.wechat_auth.settings.session_signing_secret", "test-secret")

    token = build_session_token("wx-openid-001") + "tampered"

    try:
        parse_session_token(token)
    except WeChatLoginError as exc:
        assert str(exc) == "invalid session token"
    else:
        raise AssertionError("expected WeChatLoginError")
