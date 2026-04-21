# Backend Scaffold And Dotnet Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Install a local .NET SDK and expand the FastAPI backend from a health-only app into a minimal modular scaffold for auth, device, binding, notification, and WebSocket entrypoints.

**Architecture:** Keep the backend intentionally small: one FastAPI app, one router per bounded area, and lightweight response models for placeholder endpoints. Follow TDD for each new route by adding API tests first, then wiring routers into the app with the least code needed to satisfy those tests.

**Tech Stack:** `uv`, `FastAPI`, `pytest`, `httpx`, `.NET SDK 8`, `WPF`

---

### Task 1: Install .NET SDK

**Files:**
- Modify: none
- Test: command verification only

**Step 1: Check package manager and current dotnet state**

Run: `winget --version` and `dotnet --list-sdks`
Expected: `winget` exists and `dotnet` shows no SDKs

**Step 2: Install the SDK**

Run: `winget install --id Microsoft.DotNet.SDK.8 --accept-source-agreements --accept-package-agreements`
Expected: install completes without interactive prompts

**Step 3: Verify installation**

Run: `dotnet --version`
Expected: a `8.x` SDK version string

### Task 2: Add failing backend scaffold tests

**Files:**
- Modify: `backend/tests/test_health.py`
- Create: `backend/tests/test_scaffold_routes.py`

**Step 1: Write failing tests for placeholder routes**

Add tests for:

```python
def test_auth_whoami_returns_placeholder():
    ...

def test_devices_returns_empty_list():
    ...

def test_binding_code_returns_placeholder_code():
    ...

def test_notifications_returns_not_implemented_payload():
    ...
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_scaffold_routes.py` from repo root or `uv run pytest tests/test_scaffold_routes.py` from `backend`
Expected: FAIL because routers or endpoints do not exist yet

### Task 3: Implement minimal backend routers

**Files:**
- Modify: `backend/src/app/main.py`
- Create: `backend/src/app/api/__init__.py`
- Create: `backend/src/app/api/router.py`
- Create: `backend/src/app/api/routes/auth.py`
- Create: `backend/src/app/api/routes/device.py`
- Create: `backend/src/app/api/routes/binding.py`
- Create: `backend/src/app/api/routes/notification.py`
- Create: `backend/src/app/api/routes/ws.py`

**Step 1: Create a central API router**

Mount one router per area under `/api`.

**Step 2: Add minimal implementations**

Use tiny placeholder responses such as:

```python
@router.get("/whoami")
def whoami() -> dict[str, str]:
    return {"user_id": "demo-user", "status": "placeholder"}
```

```python
@router.get("/devices")
def list_devices() -> dict[str, list[dict[str, str]]]:
    return {"items": []}
```

**Step 3: Include routers in `app.main`**

Register the shared API router on the FastAPI app.

### Task 4: Verify backend tests pass

**Files:**
- Modify: none
- Test: `backend/tests/test_health.py`, `backend/tests/test_scaffold_routes.py`

**Step 1: Run targeted tests**

Run: `uv run pytest`
Expected: all backend tests PASS

### Task 5: Update docs for local developer flow

**Files:**
- Modify: `backend/README.md`
- Modify: `README.md`

**Step 1: Ensure uv-first instructions are explicit**

Document:

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
uv run pytest
```

**Step 2: Mention installed .NET expectation**

Add a short note that the Windows client can be opened once `dotnet --version` succeeds.
