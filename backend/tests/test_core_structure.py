from importlib.util import find_spec

from app.core.logging import configure_logging
from app.core.settings import Settings, settings


def test_core_modules_expose_infrastructure_entrypoints() -> None:
    assert find_spec("app.core.db") is not None
    assert find_spec("app.core.settings") is not None
    assert find_spec("app.core.logging") is not None
    assert settings.app_name
    assert callable(configure_logging)


def test_settings_support_sql_echo_flag() -> None:
    parsed = Settings(sql_echo=True)

    assert parsed.sql_echo is True
