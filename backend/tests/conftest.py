import os
from pathlib import Path


TEST_DATABASE_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "pytest.sqlite3"
TEST_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
if TEST_DATABASE_PATH.exists():
    TEST_DATABASE_PATH.unlink()

os.environ["SCHOOL_NOTIFY_DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"
