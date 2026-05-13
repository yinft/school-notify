from sqlalchemy import delete

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import AdminSession, AdminUser
from app.services.admin_auth import ensure_admin_user

from fastapi.testclient import TestClient


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.execute(delete(AdminSession))
        session.execute(delete(AdminUser))
        session.commit()


def test_admin_login_rejects_unknown_user() -> None:
    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid admin credentials"}


def test_admin_login_returns_session_for_valid_credentials() -> None:
    with SessionLocal() as session:
        session.add(
            AdminUser(
                username="admin",
                password_hash="legacy-plain$pass123456",
                display_name="系统管理员",
            )
        )
        session.commit()

    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == "admin"
    assert payload["display_name"] == "系统管理员"
    assert payload["session_token"].startswith("admin-session:")


def test_admin_me_returns_current_admin() -> None:
    with SessionLocal() as session:
        session.add(
            AdminUser(
                username="admin",
                password_hash="legacy-plain$pass123456",
                display_name="系统管理员",
            )
        )
        session.commit()

    login_response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )

    response = client.get(
        "/api/admin/auth/me",
        headers={"Authorization": f"Bearer {login_response.json()['session_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "admin",
        "display_name": "系统管理员",
    }


def test_admin_logout_revokes_current_session() -> None:
    with SessionLocal() as session:
        session.add(
            AdminUser(
                username="admin",
                password_hash="legacy-plain$pass123456",
                display_name="系统管理员",
            )
        )
        session.commit()

    login_response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )
    token = login_response.json()["session_token"]

    logout_response = client.post(
        "/api/admin/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    me_response = client.get(
        "/api/admin/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert logout_response.status_code == 204
    assert me_response.status_code == 401
    assert me_response.json() == {"detail": "invalid admin session"}


def test_ensure_admin_user_bootstraps_admin_account() -> None:
    with SessionLocal() as session:
        ensure_admin_user(
            session,
            username="bootstrap-admin",
            password="bootstrap-pass",
            display_name="默认管理员",
        )
        session.commit()
        admin = session.query(AdminUser).filter(AdminUser.username == "bootstrap-admin").one()

    assert admin.username == "bootstrap-admin"
    assert admin.display_name == "默认管理员"
    assert admin.password_hash != "bootstrap-pass"
    assert not admin.password_hash.startswith("plain$")
    assert not admin.password_hash.startswith("legacy-plain$")


def test_admin_login_upgrades_legacy_plain_password_hash() -> None:
    with SessionLocal() as session:
        session.add(
            AdminUser(
                username="admin",
                password_hash="legacy-plain$pass123456",
                display_name="系统管理员",
            )
        )
        session.commit()

    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )

    assert response.status_code == 200

    with SessionLocal() as session:
        admin = session.query(AdminUser).filter(AdminUser.username == "admin").one()

    assert not admin.password_hash.startswith("legacy-plain$")
    assert not admin.password_hash.startswith("plain$")
