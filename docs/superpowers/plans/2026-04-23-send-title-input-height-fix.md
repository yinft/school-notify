# Send Title Input Height Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the title input height on the miniapp send notification page without affecting shared input styles on other pages.

**Architecture:** Use a page-scoped CSS class on the send page title input and define explicit single-line input sizing in the send page stylesheet. Keep the global `.field-input` rule unchanged so the fix remains isolated to the affected control.

**Tech Stack:** WeChat Mini Program WXML, WXSS

---

### Task 1: Scope The Title Input Fix To The Send Page

**Files:**
- Modify: `miniapp/pages/send/index.wxml`
- Modify: `miniapp/pages/send/index.wxss`

- [ ] **Step 1: Confirm there is no automated UI test covering this input**

Check the existing miniapp tests and page files to confirm this is a view-only style fix with no current UI automation coverage.

- [ ] **Step 2: Add a dedicated class to the title input in `miniapp/pages/send/index.wxml`**

Change the title input from:

```xml
<input class="field-input" placeholder="例如：下午三点全体班委集合" bindinput="onTitleInput" value="{{title}}" />
```

to:

```xml
<input class="field-input send-title-input" placeholder="例如：下午三点全体班委集合" bindinput="onTitleInput" value="{{title}}" />
```

- [ ] **Step 3: Add minimal page-scoped height rules in `miniapp/pages/send/index.wxss`**

Add a dedicated rule:

```css
.send-title-input {
  height: 88rpx;
  line-height: 44rpx;
  box-sizing: border-box;
}
```

If visual testing in the WeChat developer tools still shows vertical misalignment, extend only this rule with:

```css
  padding-top: 22rpx;
  padding-bottom: 22rpx;
```

- [ ] **Step 4: Verify only the intended files changed**

Run: `git diff -- miniapp/pages/send/index.wxml miniapp/pages/send/index.wxss`

Expected: The diff shows only the added `send-title-input` class in WXML and the new `.send-title-input` rule in WXSS.

- [ ] **Step 5: Manual verification in WeChat DevTools**

Open the send page and confirm:
- the title input height looks normal
- the body textarea remains unchanged
- the bind page input remains unchanged
- the custom duration input remains unchanged
