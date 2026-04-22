from fastapi.testclient import TestClient

from app import settings as app_settings

app_settings.settings.database_url = "sqlite:///./test_school_notify.db"

from app.main import app


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "school-notify-backend"}
