from importlib.util import find_spec

from app.core.logging import configure_logging
from app.core.settings import settings


def test_core_modules_expose_infrastructure_entrypoints() -> None:
    assert find_spec("app.core.db") is not None
    assert find_spec("app.core.settings") is not None
    assert find_spec("app.core.logging") is not None
    assert settings.app_name
    assert callable(configure_logging)
