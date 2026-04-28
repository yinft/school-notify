from app.core.settings import settings
from app.services import store as store_module


def test_pytest_uses_sqlite_database() -> None:
    assert settings.database_url.startswith("sqlite:///")


def test_store_reset_refuses_non_sqlite_database(monkeypatch) -> None:
    monkeypatch.setattr(store_module.settings, "database_url", "postgresql+psycopg://example/prod")

    try:
        try:
            store_module.store.reset()
        except RuntimeError as exc:
            assert "Refusing to reset non-SQLite database" in str(exc)
        else:
            raise AssertionError("store.reset should refuse non-SQLite databases")
    finally:
        monkeypatch.setattr(store_module.settings, "database_url", settings.database_url)
