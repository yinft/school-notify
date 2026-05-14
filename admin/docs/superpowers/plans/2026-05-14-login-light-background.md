# Login Light Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the admin login page to use a bright blue-white background and light cards without changing layout or behavior.

**Architecture:** The change stays inside the existing login-specific CSS block in `src/styles/main.css`. The two-column template, form markup, and router/auth behavior remain untouched while color, border, shadow, and gradient values are adjusted to create a lighter presentation.

**Tech Stack:** Vue 3, Vite, Element Plus, global CSS

---

## File Structure

- Modify: `src/styles/main.css`
  - Owns the login page shell, hero, panel, and card presentation.
  - No template change is planned because the existing selectors already isolate the login page.

### Task 1: Lighten The Login Shell And Hero

**Files:**
- Modify: `src/styles/main.css:385-439`

- [ ] **Step 1: Update the login shell and hero background values**

Replace the existing login styles in `src/styles/main.css` with the following block:

```css
.login-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.login-hero,
.login-panel {
  display: grid;
  place-items: center;
  padding: 36px;
}

.login-hero {
  background:
    radial-gradient(circle at 20% 18%, rgba(255, 255, 255, 0.92), transparent 20%),
    radial-gradient(circle at 78% 12%, rgba(162, 198, 255, 0.36), transparent 24%),
    linear-gradient(160deg, #f2f7ff 0%, #dfeeff 55%, #cfe3ff 100%);
}

.login-brand-card,
.login-card {
  width: min(100%, 460px);
  padding: 34px;
  border-radius: 28px;
}
```

- [ ] **Step 2: Verify the edited CSS block is present and scoped correctly**

Read `src/styles/main.css` around the login styles and confirm:

```text
- `.login-shell` now includes a light page background gradient.
- `.login-hero` now uses a pale blue gradient instead of the dark blue gradient.
- Shared layout and spacing values are unchanged.
```

- [ ] **Step 3: Commit the shell and hero update**

```bash
git add src/styles/main.css
git commit -m "style: lighten login page background"
```

### Task 2: Convert The Brand Card And Login Card To Light Surfaces

**Files:**
- Modify: `src/styles/main.css:412-446`

- [ ] **Step 1: Update the card surface, text, border, and panel values**

Adjust the remaining login-specific selectors in `src/styles/main.css` to the following values:

```css
.login-brand-card {
  color: #16325c;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 0 24px 60px rgba(84, 122, 191, 0.18);
  backdrop-filter: blur(18px);
}

.login-brand-card p {
  margin: 0;
  color: rgba(22, 50, 92, 0.66);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 12px;
}

.login-brand-card span {
  color: rgba(22, 50, 92, 0.78);
}

.login-panel {
  background: rgba(255, 255, 255, 0.34);
}

.login-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(214, 227, 246, 0.95);
  box-shadow: 0 28px 64px rgba(76, 108, 168, 0.14);
}

.login-card .primary-button {
  width: 100%;
  margin-top: 8px;
}

.login-hint {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
}
```

- [ ] **Step 2: Check for text contrast regressions in the selector set**

Read `src/styles/main.css` and confirm:

```text
- `.login-brand-card` text color is dark enough for a light card.
- `.login-brand-card p` and `.login-brand-card span` use muted dark text, not white.
- `.login-card` has either a border, shadow, or both to preserve depth on a light page.
```

- [ ] **Step 3: Commit the card styling update**

```bash
git add src/styles/main.css
git commit -m "style: refresh login cards for light theme"
```

### Task 3: Verify Responsive Behavior And Final Diff

**Files:**
- Modify: `src/styles/main.css` if follow-up tweaks are needed

- [ ] **Step 1: Run the project locally and inspect the login page**

Run:

```bash
npm run dev
```

Expected:

```text
Vite dev server starts successfully and serves the admin app locally.
```

Open the login page and verify:

```text
- Desktop keeps the current two-column composition.
- The hero side reads as light blue, not dark blue.
- The brand card and form card are both clearly legible and visually separated.
```

- [ ] **Step 2: Verify the mobile breakpoint still stacks correctly**

Using browser responsive mode at widths below `1100px` and `720px`, verify:

```text
- `.login-shell` still collapses to one column.
- `.login-hero` and `.login-panel` keep usable padding.
- No card overflow or clipped shadows appear on small screens.
```

- [ ] **Step 3: Review the final diff**

Run:

```bash
git diff -- src/styles/main.css
```

Expected:

```text
The diff only changes login-related selectors and does not alter unrelated admin styles.
```

- [ ] **Step 4: Commit the verified final state**

```bash
git add src/styles/main.css
git commit -m "style: brighten admin login experience"
```
