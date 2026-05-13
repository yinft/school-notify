# Admin Backend And Version Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Vue 3 admin console, add dedicated FastAPI admin and public version APIs, and let the website read published client versions from the backend.

**Architecture:** Keep the existing `backend` as the single API service, add separate `/api/admin/*` and `/api/public/versions/*` route groups, and scaffold a new `admin/` frontend that calls those endpoints. Reuse existing device, user, and notification tables for admin read operations, and add new admin auth and client version tables for the new backend capabilities.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, pytest, Nuxt 4, Vue 3, Vite, Vue Router, Pinia, Element Plus

---

## File Map

- Create: `backend/alembic/versions/20260513_01_admin_and_client_versions.py`
- Modify: `backend/src/app/models.py`
- Modify: `backend/src/app/api/router.py`
- Create: `backend/src/app/api/deps/admin_auth.py`
- Create: `backend/src/app/api/routes/admin_auth.py`
- Create: `backend/src/app/api/routes/admin_dashboard.py`
- Create: `backend/src/app/api/routes/admin_devices.py`
- Create: `backend/src/app/api/routes/admin_users.py`
- Create: `backend/src/app/api/routes/admin_notifications.py`
- Create: `backend/src/app/api/routes/admin_versions.py`
- Create: `backend/src/app/api/routes/public_versions.py`
- Create: `backend/src/app/schemas/admin_auth.py`
- Create: `backend/src/app/schemas/admin_dashboard.py`
- Create: `backend/src/app/schemas/admin_device.py`
- Create: `backend/src/app/schemas/admin_user.py`
- Create: `backend/src/app/schemas/admin_notification.py`
- Create: `backend/src/app/schemas/admin_version.py`
- Create: `backend/src/app/services/admin_auth.py`
- Create: `backend/src/app/services/admin_dashboard.py`
- Create: `backend/src/app/services/admin_queries.py`
- Create: `backend/src/app/services/admin_versions.py`
- Create: `backend/tests/test_admin_auth.py`
- Create: `backend/tests/test_admin_versions.py`
- Create: `backend/tests/test_admin_queries.py`
- Modify: `website/app/pages/index.vue`
- Modify: `website/app/data/site-content.js`
- Create: `website/server/api/versions.get.ts` or fetch directly from backend from page-level composables, depending on existing Nuxt pattern
- Create: `admin/package.json`
- Create: `admin/vite.config.ts`
- Create: `admin/index.html`
- Create: `admin/src/main.ts`
- Create: `admin/src/App.vue`
- Create: `admin/src/router/index.ts`
- Create: `admin/src/stores/auth.ts`
- Create: `admin/src/layouts/AdminLayout.vue`
- Create: `admin/src/pages/login/LoginPage.vue`
- Create: `admin/src/pages/dashboard/DashboardPage.vue`
- Create: `admin/src/pages/devices/DevicesPage.vue`
- Create: `admin/src/pages/users/UsersPage.vue`
- Create: `admin/src/pages/notifications/NotificationsPage.vue`
- Create: `admin/src/pages/versions/VersionsPage.vue`
- Create: `admin/src/services/http.ts`
- Create: `admin/src/services/adminAuth.ts`
- Create: `admin/src/services/adminDashboard.ts`
- Create: `admin/src/services/adminDevices.ts`
- Create: `admin/src/services/adminUsers.ts`
- Create: `admin/src/services/adminNotifications.ts`
- Create: `admin/src/services/adminVersions.ts`
- Create: `admin/src/styles/main.css`
- Copy or reference existing product icon under `admin/public/`

### Task 1: Backend admin auth foundation

**Files:**
- Create: `backend/tests/test_admin_auth.py`
- Modify: `backend/src/app/models.py`
- Create: `backend/src/app/services/admin_auth.py`
- Create: `backend/src/app/schemas/admin_auth.py`
- Create: `backend/src/app/api/deps/admin_auth.py`
- Create: `backend/src/app/api/routes/admin_auth.py`
- Modify: `backend/src/app/api/router.py`
- Create: `backend/alembic/versions/20260513_01_admin_and_client_versions.py`

- [ ] Step 1: Write failing admin auth tests for login, logout, and current admin.
- [ ] Step 2: Run `uv run pytest backend/tests/test_admin_auth.py -v` from `backend` and verify failures mention missing routes or models.
- [ ] Step 3: Add `AdminUser` and `AdminSession` SQLAlchemy models plus migration.
- [ ] Step 4: Implement minimal admin auth service with password check and session creation.
- [ ] Step 5: Implement admin auth dependency and routes.
- [ ] Step 6: Run `uv run pytest backend/tests/test_admin_auth.py -v` and make it pass.

### Task 2: Backend client version management

**Files:**
- Create: `backend/tests/test_admin_versions.py`
- Modify: `backend/src/app/models.py`
- Create: `backend/src/app/services/admin_versions.py`
- Create: `backend/src/app/schemas/admin_version.py`
- Create: `backend/src/app/api/routes/admin_versions.py`
- Create: `backend/src/app/api/routes/public_versions.py`
- Modify: `backend/src/app/api/router.py`
- Modify: `backend/alembic/versions/20260513_01_admin_and_client_versions.py`

- [ ] Step 1: Write failing tests for create, list, publish, recommend, delete rules, and public filtering.
- [ ] Step 2: Run `uv run pytest backend/tests/test_admin_versions.py -v` and verify expected failures.
- [ ] Step 3: Add `ClientVersion` model and migration statements.
- [ ] Step 4: Implement minimal version service and admin/public routes.
- [ ] Step 5: Run `uv run pytest backend/tests/test_admin_versions.py -v` and make it pass.

### Task 3: Backend admin dashboard, devices, users, and notifications queries

**Files:**
- Create: `backend/tests/test_admin_queries.py`
- Create: `backend/src/app/services/admin_dashboard.py`
- Create: `backend/src/app/services/admin_queries.py`
- Create: `backend/src/app/schemas/admin_dashboard.py`
- Create: `backend/src/app/schemas/admin_device.py`
- Create: `backend/src/app/schemas/admin_user.py`
- Create: `backend/src/app/schemas/admin_notification.py`
- Create: `backend/src/app/api/routes/admin_dashboard.py`
- Create: `backend/src/app/api/routes/admin_devices.py`
- Create: `backend/src/app/api/routes/admin_users.py`
- Create: `backend/src/app/api/routes/admin_notifications.py`
- Modify: `backend/src/app/api/router.py`

- [ ] Step 1: Write failing tests for dashboard summary, device list/detail/update/unbind, user list/detail, and notification list/detail.
- [ ] Step 2: Run `uv run pytest backend/tests/test_admin_queries.py -v` and verify failures.
- [ ] Step 3: Implement minimal query services and routes using existing tables.
- [ ] Step 4: Run `uv run pytest backend/tests/test_admin_queries.py -v` and make it pass.

### Task 4: Website published version integration

**Files:**
- Modify: `website/app/pages/index.vue`
- Modify: `website/app/data/site-content.js`
- Create or modify minimal Nuxt fetch helper if needed

- [ ] Step 1: Add a failing website test or adapt existing site-content test to expect backend-driven release data shape.
- [ ] Step 2: Run `npm test` in `website` and verify failure.
- [ ] Step 3: Replace hardcoded release rendering with data fetched from the public version API, keeping existing icon and layout.
- [ ] Step 4: Run `npm test` in `website` and make it pass.

### Task 5: Admin frontend scaffold and auth shell

**Files:**
- Create: `admin/package.json`
- Create: `admin/vite.config.ts`
- Create: `admin/index.html`
- Create: `admin/src/main.ts`
- Create: `admin/src/App.vue`
- Create: `admin/src/router/index.ts`
- Create: `admin/src/stores/auth.ts`
- Create: `admin/src/layouts/AdminLayout.vue`
- Create: `admin/src/pages/login/LoginPage.vue`
- Create: `admin/src/styles/main.css`
- Create: `admin/src/services/http.ts`
- Create: `admin/src/services/adminAuth.ts`

- [ ] Step 1: Create the admin app scaffold with one failing smoke test if practical; otherwise use build as the verification gate.
- [ ] Step 2: Run `npm install` then `npm run build` in `admin` and verify it fails before implementation is complete.
- [ ] Step 3: Implement the login page, auth store, route guard, shell layout, and brand icon integration.
- [ ] Step 4: Run `npm run build` in `admin` and make it pass.

### Task 6: Admin version management page

**Files:**
- Create: `admin/src/services/adminVersions.ts`
- Create: `admin/src/pages/versions/VersionsPage.vue`
- Modify: `admin/src/router/index.ts`
- Modify: `admin/src/layouts/AdminLayout.vue`

- [ ] Step 1: Build the version list and create/edit/publish/recommend UI against the finished backend API.
- [ ] Step 2: Run `npm run build` in `admin` and keep it green.

### Task 7: Admin dashboard, device, user, and notification pages

**Files:**
- Create: `admin/src/services/adminDashboard.ts`
- Create: `admin/src/services/adminDevices.ts`
- Create: `admin/src/services/adminUsers.ts`
- Create: `admin/src/services/adminNotifications.ts`
- Create: `admin/src/pages/dashboard/DashboardPage.vue`
- Create: `admin/src/pages/devices/DevicesPage.vue`
- Create: `admin/src/pages/users/UsersPage.vue`
- Create: `admin/src/pages/notifications/NotificationsPage.vue`
- Modify: `admin/src/router/index.ts`
- Modify: `admin/src/layouts/AdminLayout.vue`

- [ ] Step 1: Implement dashboard charts and cards.
- [ ] Step 2: Implement device, user, and notification pages with filters, tables, and detail drawers.
- [ ] Step 3: Run `npm run build` in `admin` and make it pass.

### Task 8: Final verification

**Files:**
- Modify only files touched by prior tasks

- [ ] Step 1: Run `uv run pytest` in `backend`.
- [ ] Step 2: Run `npm test` in `website`.
- [ ] Step 3: Run `npm run build` in `website`.
- [ ] Step 4: Run `npm run build` in `admin`.
- [ ] Step 5: Fix any failures without broadening scope.
