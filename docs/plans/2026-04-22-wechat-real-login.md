# WeChat Real Login Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the mock miniapp login with a real WeChat `code2Session` backend flow and use `openid` as the system `user_id`.

**Architecture:** The miniapp continues to call `wx.login`, but the backend `POST /api/auth/login` now exchanges the code with WeChat's `code2Session` API using environment variables for credentials. The backend returns a normalized auth session payload whose `user_id` is the WeChat `openid`, and the miniapp stores and uses that value in the existing login state flow.

**Tech Stack:** FastAPI, httpx, pydantic-settings, WeChat miniapp `wx.login`, Node test runner, pytest.

---

### Task 1: Add backend tests for real login behavior

**Files:**
- Modify: `backend/tests/test_scaffold_routes.py`
- Test: `backend/tests/test_scaffold_routes.py`

**Step 1: Write the failing test**
- Add a test asserting `POST /api/auth/login` returns `openid` as `user_id` when the WeChat exchange succeeds.
- Add a test asserting the route returns a 502-style error when the WeChat exchange fails or omits `openid`.

**Step 2: Run test to verify it fails**
- Run: `uv run pytest tests/test_scaffold_routes.py -q`
- Expected: auth tests fail because the backend still returns the mock payload.

**Step 3: Write minimal implementation**
- Add a WeChat auth service wrapper around `code2Session`.
- Wire `auth.py` route to the service.

**Step 4: Run test to verify it passes**
- Run: `uv run pytest tests/test_scaffold_routes.py -q`
- Expected: auth tests pass.

### Task 2: Add backend auth config and HTTP client call

**Files:**
- Modify: `backend/src/app/settings.py`
- Create: `backend/src/app/services/wechat_auth.py`
- Modify: `backend/src/app/api/routes/auth.py`
- Modify: `backend/src/app/schemas/auth.py`

**Step 1: Add config inputs**
- Add `wechat_app_id`, `wechat_app_secret`, and `wechat_code2session_url` settings.

**Step 2: Add exchange service**
- Implement a small async/sync helper that calls WeChat with `appid`, `secret`, `js_code`, `grant_type=authorization_code`.
- Validate `openid` exists.

**Step 3: Normalize backend response**
- Keep `session_token` and `auth_provider` fields.
- Return `openid` as `user_id`.

**Step 4: Re-run backend tests**
- Run: `uv run pytest -q`
- Expected: all backend tests stay green.

### Task 3: Add miniapp coverage for the auth payload mapping

**Files:**
- Modify: `miniapp/tests/api.test.js`
- Modify: `miniapp/services/auth.js`

**Step 1: Write the failing test**
- Assert the auth service maps backend `user_id`, `session_token`, and `auth_provider` correctly.

**Step 2: Run test to verify it fails**
- Run: `npm test`
- Expected: failure if the mapping or file is missing.

**Step 3: Write minimal implementation**
- Keep the miniapp auth service thin and pass through the normalized backend session.

**Step 4: Run test to verify it passes**
- Run: `npm test`
- Expected: all miniapp tests pass.

### Task 4: Document environment-based setup

**Files:**
- Modify: `backend/README.md`
- Modify: `miniapp/README.md`

**Step 1: Add backend env setup**
- Document `SCHOOL_NOTIFY_WECHAT_APP_ID` and `SCHOOL_NOTIFY_WECHAT_APP_SECRET`.

**Step 2: Add miniapp note**
- Clarify that miniapp login now depends on backend WeChat auth configuration.

**Step 3: Run final verification**
- Run: `uv run pytest -q`
- Run: `npm test`
- Expected: both green.
