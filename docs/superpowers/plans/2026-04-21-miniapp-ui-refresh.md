# Miniapp UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the miniapp UI with a unified campus-themed visual system and small interaction upgrades without changing backend behavior.

**Architecture:** Keep the current page structure and service layer, push most changes into shared WXSS tokens and targeted WXML rewrites, and use only minimal page-level JS to support retry actions, summary data, and send-page selection helpers. Preserve existing request contracts and navigation patterns.

**Tech Stack:** WeChat Mini Program (`wxml`, `wxss`, `js`), Node built-in test runner

---

### Task 1: Extend data mapping for record timestamps

**Files:**
- Modify: `miniapp/tests/api.test.js`
- Modify: `miniapp/services/notification.js`

- [x] Add a failing test for `created_at` mapping in notification records.
- [x] Run `npm test -- tests/api.test.js` and verify the new test fails because `createdAt` is missing.
- [x] Add `createdAt: item.created_at` to the record mapper.
- [x] Re-run `npm test -- tests/api.test.js` after the UI work is complete.

### Task 2: Build shared visual tokens and tab shell

**Files:**
- Modify: `miniapp/app.wxss`
- Modify: `miniapp/custom-tab-bar/index.js`
- Modify: `miniapp/custom-tab-bar/index.wxml`
- Modify: `miniapp/custom-tab-bar/index.wxss`

- [x] Replace the old neutral theme with shared hero, button, field, state-panel, badge, and spacing styles.
- [x] Replace emoji tab icons with stable text-symbol styling and a stronger selected state.

### Task 3: Refresh device and send pages

**Files:**
- Modify: `miniapp/pages/devices/index.wxml`
- Modify: `miniapp/pages/devices/index.wxss`
- Modify: `miniapp/pages/devices/index.js`
- Modify: `miniapp/pages/send/index.wxml`
- Modify: `miniapp/pages/send/index.wxss`
- Modify: `miniapp/pages/send/index.js`
- Modify: `miniapp/pages/send/index.json`

- [x] Add hero summaries, unified empty/error states, and main action styling to devices.
- [x] Add hero summary, selection counters, quick actions, disabled-state hints, retry flow, and pull-down refresh to send.

### Task 4: Refresh records, profile, and bind pages

**Files:**
- Modify: `miniapp/pages/records/index.wxml`
- Modify: `miniapp/pages/records/index.wxss`
- Modify: `miniapp/pages/records/index.js`
- Modify: `miniapp/pages/profile/index.wxml`
- Modify: `miniapp/pages/profile/index.wxss`
- Modify: `miniapp/pages/bind/index.wxml`
- Modify: `miniapp/pages/bind/index.wxss`

- [x] Add hero summaries and readable record metadata, including optional created-at text.
- [x] Align profile and bind pages with the shared visual system.

### Task 5: Verify changes

**Files:**
- Verify: `miniapp/tests/api.test.js`
- Verify: modified miniapp UI files above

- [ ] Run `npm test -- tests/api.test.js` and confirm all tests pass.
- [ ] Inspect the final diff for accidental scope creep or syntax mistakes.
