# Miniapp Scroll Containment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make miniapp pages stop scrolling as whole pages and move vertical scrolling into a shared inner content region.

**Architecture:** Convert the shared `.page` shell into a fixed-height flex container and introduce a reusable `.page-body` scroll region. Update each existing miniapp page so only its non-login content renders inside that scroll region.

**Tech Stack:** WeChat Mini Program WXML, WXSS

---

### Task 1: Add shared fixed page shell styles

**Files:**
- Modify: `miniapp/app.wxss`

- [ ] **Step 1: Update the global page shell styles**

Add a fixed-height flex layout for `.page` and a reusable `.page-body` scroll container while preserving the existing safe-area padding.

- [ ] **Step 2: Keep login layout isolated**

Retain login-specific clipping and padding on `.page-login` so the login gate continues to use the current full-screen presentation.

### Task 2: Move non-login page content into the shared scroll region

**Files:**
- Modify: `miniapp/pages/devices/index.wxml`
- Modify: `miniapp/pages/bind/index.wxml`
- Modify: `miniapp/pages/send/index.wxml`
- Modify: `miniapp/pages/records/index.wxml`
- Modify: `miniapp/pages/profile/index.wxml`

- [ ] **Step 1: Wrap non-login content in `page-body`**

For each page, keep the top-level `.page` wrapper and login branch unchanged, and wrap the `wx:else` page content in `<view class="page-body">...</view>`.

- [ ] **Step 2: Preserve existing page ordering and spacing**

Do not alter card order, section hierarchy, bindings, or existing page-specific classes while moving content into the new scroll region.

### Task 3: Verify layout assumptions

**Files:**
- Review: `miniapp/components/native-title-bar/index.wxml`
- Review: `miniapp/components/native-title-bar/index.wxss`

- [ ] **Step 1: Confirm title bar remains outside the scroll container**

Ensure each page still renders `native-title-bar` before `.page`, so only page content scrolls.

- [ ] **Step 2: Manually verify overflow ownership**

Check that the only vertical scrolling owner is `.page-body`, not the outer page shell.
