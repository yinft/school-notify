# Admin Responsive Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the admin UI so it is responsive, table-safe, aligned, and visually upgraded.

**Architecture:** Keep the existing Vue pages and Element Plus components. Add shared CSS primitives for shell layout, responsive grids, table scroll wrappers, table action groups, and polished card/table/form styling.

**Tech Stack:** Vue 3, Vite, TypeScript, Element Plus, CSS Grid/Flex, Node static test.

---

### Task 1: Static Regression Test

**Files:**
- Create: `admin/tests/admin-responsive-structure.test.mjs`
- Modify: `admin/package.json`

- [ ] Add a Node script that reads the admin Vue/CSS files and asserts list tables are wrapped in `.table-scroll`, table actions use `.table-actions`, and CSS includes required responsive primitives.
- [ ] Add `test:ui` script to run the static test.
- [ ] Run `npm run test:ui` and verify it fails before implementation because wrappers/classes are missing.

### Task 2: Page Structure

**Files:**
- Modify: `admin/src/layouts/AdminLayout.vue`
- Modify: `admin/src/pages/devices/DevicesPage.vue`
- Modify: `admin/src/pages/users/UsersPage.vue`
- Modify: `admin/src/pages/notifications/NotificationsPage.vue`
- Modify: `admin/src/pages/versions/VersionsPage.vue`
- Modify: `admin/src/pages/dashboard/DashboardPage.vue`
- Modify: `admin/src/pages/login/LoginPage.vue`

- [ ] Add shell affordances for responsive navigation and stronger topbar identity.
- [ ] Wrap each list `el-table` in `.table-scroll`.
- [ ] Add `.table-actions` around operation buttons.
- [ ] Apply overflow tooltip and alignment classes to long table columns.
- [ ] Keep existing data loading and mutation logic unchanged.

### Task 3: Visual System CSS

**Files:**
- Modify: `admin/src/styles/main.css`

- [ ] Update design tokens for blue-green console styling.
- [ ] Add responsive shell, card, filter, table, drawer, dialog, dashboard, and login styles.
- [ ] Add media queries at desktop, tablet, and phone widths.
- [ ] Ensure tables scroll inside cards and small-screen filters stack cleanly.

### Task 4: Verification

**Files:**
- No source files expected unless verification exposes an issue.

- [ ] Run `npm run test:ui` from `admin`; expected pass.
- [ ] Run `npm run build` from `admin`; expected pass.
- [ ] Review `git diff` to confirm only intended admin UI files and docs changed.
