# Table Action Link Buttons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all admin table action buttons readable by switching them to Element Plus native `link` buttons and removing custom version-table button skinning.

**Architecture:** Keep the existing table structure and action semantics. Update the static structure test first, then change the Vue templates from `text` to `link`, and finally delete the CSS overrides that were restyling version-table action buttons away from Element Plus defaults.

**Tech Stack:** Vue 3, Vite, Element Plus, CSS, Node static test.

---

### Task 1: Add Static Coverage For Link Buttons

**Files:**
- Modify: `tests/admin-responsive-structure.test.mjs`

- [ ] Add assertions that each list page contains at least one `el-button` using the `link` attribute inside table action areas.
- [ ] Run `npm run test:ui`.
- [ ] Verify the test fails before implementation because current table actions still use `text` buttons.

### Task 2: Switch Table Action Buttons To Element Plus Link Buttons

**Files:**
- Modify: `src/pages/devices/DevicesPage.vue`
- Modify: `src/pages/users/UsersPage.vue`
- Modify: `src/pages/notifications/NotificationsPage.vue`
- Modify: `src/pages/versions/VersionsPage.vue`

- [ ] Replace table operation `el-button text` usage with `el-button link`.
- [ ] Keep existing icons, click handlers, conditions, and semantic `type` props unchanged.
- [ ] Avoid changing non-table buttons such as dialog actions, retry buttons, or drawer utility buttons.

### Task 3: Remove Version-Specific Button Skinning

**Files:**
- Modify: `src/styles/main.css`

- [ ] Delete `.version-table .table-actions` button color/background/border overrides.
- [ ] Keep `.table-actions` and `.table-actions-wide` layout rules intact.

### Task 4: Verify The UI Build And Static Checks

**Files:**
- No source files expected unless verification exposes an issue.

- [ ] Run `npm run test:ui` and verify it passes.
- [ ] Run `npm run build` and verify it passes.
- [ ] Review the resulting diff to confirm only intended table-action files, CSS, and docs changed.
