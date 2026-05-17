# Version And Admin UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align website/client version selection behavior and polish the admin version management UI and related list-page interactions.

**Architecture:** Keep the current backend recommendation model for device heartbeat updates, tighten website version-content selection to prefer recommended versions with a latest-published fallback, and improve admin pages in place using existing Element Plus patterns and shared CSS utilities. Add the smallest targeted tests around website version content generation and heartbeat update behavior.

**Tech Stack:** Nuxt/Vue, Element Plus, Node test runner, FastAPI pytest

---

### Task 1: Lock website version selection behavior with tests

**Files:**
- Create: `website/app/data/version-content.test.js`
- Modify: `website/app/data/version-content.js`

- [ ] Add tests covering recommended-version preference and release truncation.
- [ ] Run `npm test -- app/data/version-content.test.js` in `website/` and confirm failure before implementation.
- [ ] Implement the minimal selection logic and release slicing in `version-content.js`.
- [ ] Re-run `npm test -- app/data/version-content.test.js` and confirm pass.

### Task 2: Lock heartbeat fallback behavior with tests

**Files:**
- Modify: `backend/tests/test_scaffold_routes.py`

- [ ] Add a test covering heartbeat behavior when published versions exist but no version is recommended.
- [ ] Run `python -m pytest tests/test_scaffold_routes.py::test_device_heartbeat_ignores_published_versions_without_recommendation -v` in `backend/` and confirm failure before implementation if behavior differs.
- [ ] Keep or minimally adjust backend implementation only if needed to satisfy the intended behavior.
- [ ] Re-run the targeted pytest command and confirm pass.

### Task 3: Polish admin version management page

**Files:**
- Modify: `admin/src/pages/versions/VersionsPage.vue`
- Modify: `admin/src/styles/main.css`

- [ ] Redesign the page header, helper copy, filter layout, table status presentation, and dialog form density.
- [ ] Use color-coded Element Plus tags for draft/published/recommended states.
- [ ] Add clearer action grouping and keep the form width constrained inside the dialog.
- [ ] Build the admin app with `npm run build` in `admin/` and fix any compile issues.

### Task 4: Replace native prompt and unify list-page filters

**Files:**
- Modify: `admin/src/pages/devices/DevicesPage.vue`
- Modify: `admin/src/pages/users/UsersPage.vue`
- Modify: `admin/src/pages/notifications/NotificationsPage.vue`
- Modify: `admin/src/styles/main.css`

- [ ] Replace the device rename `window.prompt` flow with an Element Plus dialog.
- [ ] Apply a shared compact filter-bar layout across devices, users, notifications, and versions.
- [ ] Keep changes minimal and consistent with existing admin structure.
- [ ] Re-run `npm run build` in `admin/` and confirm success.
