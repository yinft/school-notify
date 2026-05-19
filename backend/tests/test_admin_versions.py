from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import AdminSession, AdminUser, ClientVersion


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.execute(delete(ClientVersion))
        session.execute(delete(AdminSession))
        session.execute(delete(AdminUser))
        session.commit()


def create_admin_and_login() -> str:
    with SessionLocal() as session:
        existing = session.query(AdminUser).filter(AdminUser.username == "admin").one_or_none()
        if existing is None:
            session.add(
                AdminUser(
                    username="admin",
                    password_hash="plain$pass123456",
                    display_name="系统管理员",
                )
            )
        session.commit()

    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )
    return response.json()["session_token"]


def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {create_admin_and_login()}"}


def test_admin_can_create_and_list_versions() -> None:
    create_response = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["is_published"] is False

    list_response = client.get("/api/admin/versions", headers=admin_headers())

    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert list_response.json()["items"][0]["version"] == "1.0.0"
    assert list_response.json()["total"] == 1
    assert list_response.json()["page"] == 1
    assert list_response.json()["page_size"] == 20


def test_admin_version_list_supports_keyword_and_pagination() -> None:
    for item in [
        {
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
        {
            "platform": "windows",
            "version": "1.1.0",
            "build_number": "110",
            "release_notes": "会议室版本",
            "download_url": "https://example.com/windows-1.1.0.zip",
            "file_size": 2048,
        },
        {
            "platform": "windows",
            "version": "1.2.0",
            "build_number": "120",
            "release_notes": "值班室版本",
            "download_url": "https://example.com/windows-1.2.0.zip",
            "file_size": 4096,
        },
    ]:
        client.post("/api/admin/versions", headers=admin_headers(), json=item)

    keyword_response = client.get("/api/admin/versions?keyword=值班&page=1&page_size=10", headers=admin_headers())
    page_response = client.get("/api/admin/versions?page=2&page_size=1", headers=admin_headers())

    assert keyword_response.status_code == 200
    assert [item["version"] for item in keyword_response.json()["items"]] == ["1.2.0"]
    assert page_response.status_code == 200
    assert page_response.json()["total"] == 3
    assert page_response.json()["page"] == 2
    assert page_response.json()["page_size"] == 1
    assert [item["version"] for item in page_response.json()["items"]] == ["1.1.0"]


def test_publish_and_recommend_version() -> None:
    create_response = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    )
    version_id = create_response.json()["id"]

    publish_response = client.post(f"/api/admin/versions/{version_id}/publish", headers=admin_headers())
    recommend_response = client.post(f"/api/admin/versions/{version_id}/recommend", headers=admin_headers())

    assert publish_response.status_code == 200
    assert publish_response.json()["is_published"] is True
    assert recommend_response.status_code == 200
    assert recommend_response.json()["is_recommended"] is True


def test_admin_rejects_version_with_v_prefix() -> None:
    response = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "v1",
            "build_number": "100",
            "release_notes": "bad version format",
            "download_url": "https://example.com/windows-v1.zip",
            "file_size": 1024,
        },
    )

    assert response.status_code == 422
    assert "version must use numeric dot notation like 1.0.0" in response.text


def test_cannot_delete_published_version() -> None:
    create_response = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    )
    version_id = create_response.json()["id"]

    client.post(f"/api/admin/versions/{version_id}/publish", headers=admin_headers())
    delete_response = client.delete(f"/api/admin/versions/{version_id}", headers=admin_headers())

    assert delete_response.status_code == 409
    assert delete_response.json() == {"detail": "published version cannot be deleted"}


def test_public_versions_only_returns_published_items() -> None:
    first_id = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    ).json()["id"]
    client.post(f"/api/admin/versions/{first_id}/publish", headers=admin_headers())

    client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.1.0",
            "build_number": "110",
            "release_notes": "未发布版本",
            "download_url": "https://example.com/windows-1.1.0.zip",
            "file_size": 2048,
        },
    )

    response = client.get("/api/public/versions?platform=windows")

    assert response.status_code == 200
    assert [item["version"] for item in response.json()["items"]] == ["1.0.0"]


def test_public_recommended_version_returns_single_item() -> None:
    version_id = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "初始版本",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    ).json()["id"]
    client.post(f"/api/admin/versions/{version_id}/publish", headers=admin_headers())
    client.post(f"/api/admin/versions/{version_id}/recommend", headers=admin_headers())

    response = client.get("/api/public/versions/recommended?platform=windows")

    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_public_versions_include_recommendation_flag() -> None:
    first_id = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.0.0",
            "build_number": "100",
            "release_notes": "stable",
            "download_url": "https://example.com/windows-1.0.0.zip",
            "file_size": 1024,
        },
    ).json()["id"]
    second_id = client.post(
        "/api/admin/versions",
        headers=admin_headers(),
        json={
            "platform": "windows",
            "version": "1.1.0",
            "build_number": "110",
            "release_notes": "candidate",
            "download_url": "https://example.com/windows-1.1.0.zip",
            "file_size": 2048,
        },
    ).json()["id"]

    client.post(f"/api/admin/versions/{first_id}/publish", headers=admin_headers())
    client.post(f"/api/admin/versions/{second_id}/publish", headers=admin_headers())
    client.post(f"/api/admin/versions/{first_id}/recommend", headers=admin_headers())

    response = client.get("/api/public/versions?platform=windows")
    items = response.json()["items"]

    assert response.status_code == 200
    assert len(items) == 2
    assert items[0]["version"] == "1.1.0"
    assert items[0]["is_recommended"] is False
    assert items[1]["version"] == "1.0.0"
    assert items[1]["is_recommended"] is True
