# Backend Core Layout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move backend infrastructure modules into `app/core` so `app/main.py` stays thin and the top-level package is less cluttered.

**Architecture:** Keep the existing backend layering intact and only relocate shared infrastructure concerns. `main.py` remains the app entrypoint, while settings, DB wiring, and logging live under `app/core` with import paths updated in-place.

**Tech Stack:** FastAPI, SQLAlchemy, pydantic-settings, Python logging, pytest.

---

### Task 1: Lock the target import structure with tests

**Files:**
- Create: `backend/tests/test_core_structure.py`
- Test: `backend/tests/test_core_structure.py`

**Step 1: Write the failing test**
- Add a test that imports `app.core.settings`, `app.core.db`, and `app.core.logging`.
- Assert the modules expose `settings`, `SessionLocal`, `get_db_session`, and `configure_logging`.

**Step 2: Run test to verify it fails**
- Run: `py -m pytest tests/test_core_structure.py -q`
- Expected: import failure because `app.core` does not exist yet.

**Step 3: Write minimal implementation**
- Create `backend/src/app/core/` and move the three infrastructure modules into it.
- Update imports across backend code and tests.

**Step 4: Run test to verify it passes**
- Run: `py -m pytest tests/test_core_structure.py -q`
- Expected: the new package imports succeed.

### Task 2: Preserve logging behavior after the move

**Files:**
- Modify: `backend/tests/test_logging_config.py`
- Modify: `backend/src/app/main.py`
- Modify: `backend/src/app/core/logging.py`

**Step 1: Keep the logging regression test**
- Reuse the existing formatting test so the move does not drop millisecond timestamps.

**Step 2: Update app startup wiring**
- Import `configure_logging` from `app.core.logging`.
- Keep `main.py` focused on startup only.

**Step 3: Re-run the focused tests**
- Run: `py -m pytest tests/test_core_structure.py tests/test_logging_config.py -q`
- Expected: both tests pass.

### Task 3: Verify the moved imports compile cleanly

**Files:**
- Modify: `backend/src/app/**/*.py` where imports reference `app.db`, `app.settings`, or `app.log_config`

**Step 1: Update import paths**
- Replace direct imports with `app.core.db`, `app.core.settings`, and `app.core.logging`.

**Step 2: Run syntax verification**
- Run: `py -m py_compile src/app/main.py src/app/core/settings.py src/app/core/db.py src/app/core/logging.py`
- Expected: no output.
