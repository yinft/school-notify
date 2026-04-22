# Miniapp UI Refresh Design

## Goal

Refresh the miniapp pages with a more cohesive "campus vitality" visual language while improving core interaction clarity. Keep the current information architecture intact, avoid backend changes, and make the app feel closer to a usable internal product than a prototype.

## Scope

This design covers:

- Global visual tokens in `miniapp/app.wxss`
- Custom tab bar styling and icon treatment in `miniapp/custom-tab-bar/*`
- Unified page headers, cards, empty states, and error states across:
  - `miniapp/pages/devices/*`
  - `miniapp/pages/send/*`
  - `miniapp/pages/records/*`
  - `miniapp/pages/profile/*`
  - `miniapp/pages/bind/*`
- Small interaction upgrades for device selection and page actions

This design does not cover:

- Backend API or response shape changes
- New dependencies, icon libraries, or remote assets
- Major navigation changes
- Complex interaction redesigns such as record detail accordions

## Product Direction

The chosen direction is "campus vitality" with balanced attention to visual upgrade and interaction efficiency.

The interface should feel:

- Bright and clear instead of dark and heavy
- Friendly and energetic instead of enterprise-formal
- Structured enough for daily operational use

The design should not become decorative for its own sake. The miniapp remains a utility tool for sending and viewing campus notice content.

## Visual System

### Color

Use a light blue-white base with a fresh blue primary accent.

- Page background: a lighter blue-tinted neutral than the current gray
- Primary accent: bright academic blue
- Secondary accent: small green or yellow accents only for highlights and status support
- Text: retain dark slate for readability
- Cards: white with subtle border and soft shadow

Urgency colors remain semantic, but should be applied through badges and soft background treatments rather than text color alone.

### Shape and Spacing

- Increase consistency in corner radius across cards, buttons, and fields
- Use a small set of spacing values instead of ad hoc spacer blocks
- Replace inline spacing views with reusable structural classes

### Components

- Buttons should share one primary visual language
- Form fields should share one field style across bind and send pages
- Empty states and error panels should use consistent composition
- Summary blocks should use the same top-of-page treatment on each tab page

## Page-Level Design

### Devices Page

Keep the device list structure, but add a compact summary section above the list.

Summary content:

- Total device count
- Online device count

List changes:

- Stronger device name hierarchy
- Secondary metadata on one line where possible
- Status shown as a compact badge or chip, not only colored text
- The bind action styled as the main page action

States:

- Loading uses a calmer structured placeholder area
- Empty state includes a clearer next step to bind a device
- Error state appears in a dedicated panel with retry language

### Send Page

This page gets the most interaction improvement while keeping the same form flow.

Summary content:

- Online device count
- Selected device count

Device selection changes:

- Keep checkbox-based selection for simplicity
- Add quick actions for "select all" and "clear"
- Show explicit selected count so the default full-selection behavior is visible

Form changes:

- Use unified field styles
- Improve labels and helper tone without changing API behavior
- Present urgency options in Chinese labels while preserving existing submission values internally
- Keep duration picker, but make the displayed text more polished

Submit action:

- Stronger disabled/loading visual treatment
- Preserve current validation rules, but make the button state feel more intentional

### Records Page

Keep the record list architecture but improve scannability.

Summary content:

- Total record count

List changes:

- Strengthen title and metadata hierarchy
- Render urgency as a proper badge with readable labels
- Keep delivery rows visible, but improve contrast and rhythm
- If a timestamp already exists in data, show it; if not, do not invent data

States:

- Empty and error states use the new shared treatment

### Profile Page

Keep the current simple structure while aligning it to the new system.

Changes:

- Refresh the header card to match the shared page hero language
- Keep menu rows but improve spacing, icon container styling, and visual polish
- Keep version information simple and secondary

### Bind Page

Keep the existing single-task structure and make it clearer.

Changes:

- Apply shared summary/header treatment if it fits naturally
- Use the shared form field and button styles
- Make the scan action a secondary button instead of a plain block
- Keep the current binding flow and validation logic

## Tab Bar

Replace emoji-driven styling with a more stable and consistent visual treatment without introducing external assets.

Constraints:

- No icon library dependency
- No remote image assets

Approach:

- Use lightweight custom-drawn graphic icons instead of emoji or plain text glyphs
- Keep the icon family visually consistent across all tabs with the same stroke weight and rounded geometry
- Strengthen the selected state with a pill or highlighted background
- Keep labels readable and aligned with the fresh campus style

Graphic direction by tab:

- Devices: monitor/device outline feel
- Send: paper-plane or send-arrow feel
- Records: list or document feel
- Profile: user or badge feel

## Interaction Rules

- Preserve current navigation flows
- Preserve pull-to-refresh where already implemented
- Add a retry action where a page shows a load error if this can be done with minimal logic
- Add send-page quick selection actions with minimal new state logic
- Do not introduce animation-heavy behavior

## Visual Differentiation Between Pages

The pages should remain part of one product system, but they should not feel templated to the point of sameness.

Differentiation should come from small, page-specific details rather than a different design system per page.

### Devices Page Details

- Lean into status visibility
- Use more chip-like and structured list presentation
- Keep the page feeling operational and monitoring-oriented
- Top card should feel like a status overview, with stronger emphasis on online state than on descriptive copy
- Prefer a more dashboard-like stat arrangement than the other pages

### Send Page Details

- Lean into action and selection
- Make quick actions and selected-count feedback feel more central
- Keep the form visually clear, but slightly more energetic than the other pages
- Top card should feel like a current task header rather than a homepage banner
- Selected target count should carry more visual weight than general summary copy
- Fix the send-page top title styling if it becomes visually inconsistent with the page hierarchy
- Update duration options to: `30s`, `1分钟`, `3分钟`, `5分钟`, `10分钟`, `自定义时长`
- When `自定义时长` is selected, reveal an additional custom duration input on the page
- Custom duration should be converted to seconds before submission without changing the API contract

### Records Page Details

- Lean into chronology and summary
- Use stronger metadata framing for time and delivery results
- Make the page feel more like a communication history view than a generic list
- Top card should feel more archival or timeline-oriented than operational
- Use layout and metadata emphasis to suggest recent history rather than a live dashboard
- Redesign the record list presentation so it feels fresher and more memorable than a standard stacked list
- Keep current data intact, but use a more distinctive record-card format for title, level, summary, and delivery result presentation
- Avoid complex accordion behavior; prefer a cleaner visual form over heavier interaction
- Refine the record presentation further into a more polished "notice brief / delivery receipt" style rather than a generic archive card
- Make the layout feel more crafted and premium while preserving readability and low interaction cost

### Profile Page Details

- Lean into identity and shortcuts
- Make the top block feel more personal and less dashboard-like
- Keep the actions card simple, but distinct from the list-heavy pages
- Top card should prioritize identity, role, and account feeling over metrics
- This should be the least data-driven hero among the main tab pages
- Replace the plain avatar placeholder with WeChat user avatar after authorization when available
- Support user authorization flow for WeChat profile avatar retrieval on the profile page
- If authorization is not granted, show a tasteful default avatar state and lightweight authorization entry
- Enrich the profile hero background with subtle layered decoration so it is not only a flat color card
- After global authorization is introduced, the profile page should primarily display already-authorized identity information rather than acting as the sole authorization entry point

### Bind Page Details

- Keep it the cleanest page in the set
- Use a focused single-task visual rhythm so it does not compete with devices/send/records
- Top card should read like a guided entry step, not a summary panel

## Hero Card Differentiation Rules

The top cards across pages must not share the same composition with only text changes.

Differentiate them in three restrained dimensions at once:

- **Color emphasis:** each page can keep the same family, but the dominant accent and supporting highlights should differ clearly
- **Layout emphasis:** each card should use a different internal balance, such as stronger stat row, stronger identity block, stronger task summary, or stronger history framing
- **Information hierarchy:** the most important line in each card should change by page type, rather than always being title-first and stats-second in the same way

Target by page:

- Devices: status-first, operational overview
- Send: task-first, selected-target overview
- Records: history-first, recent-result overview
- Profile: identity-first, personal access overview
- Bind: guidance-first, single-task entry overview

## Data and Logic Constraints

- Do not change service interfaces
- Do not change request payloads
- Do not add speculative abstractions or a component system unless needed by repeated styling
- Prefer minimal JS changes and targeted WXML/WXSS updates
- WeChat avatar support should remain page-local unless later requirements ask for a broader user profile system

## Startup Authorization Gate

The app should treat WeChat user identity as a prerequisite for core functionality rather than an optional profile enhancement.

Requirements:

- On startup, check whether user profile authorization data already exists in app state or local storage
- If not authorized, show a global authorization gate before the main functional pages are usable
- The gate should explain that avatar and nickname are used to identify the current user relationship with devices and records
- The user must explicitly trigger authorization through a button interaction that calls WeChat profile retrieval
- On successful authorization, store nickname and avatar locally and in app-level state for reuse across pages
- Before authorization completes, devices, send, and records flows should not be usable as normal functional pages

Interaction model:

- Do not attempt an impermissible silent authorization on launch
- Instead, launch into a controlled entry state that immediately asks for authorization with a clear CTA
- Once authorized, transition into the normal tab-based experience

State model:

- App-level state should hold the authorized profile data
- Profile page should read from the shared app-level state
- Local storage should be used only to persist the minimal profile display fields needed on subsequent launches

## Testing and Verification

Verification should focus on:

- Existing tests still passing
- Miniapp code remaining syntactically valid
- No broken references in WXML class names after style consolidation
- Send-page quick actions preserving current selection behavior
- Tab selection still updating correctly on page show

## Implementation Strategy

Use a light-to-medium touch implementation:

1. Establish shared visual tokens and utility classes in `app.wxss`
2. Refresh the tab bar so the global shell sets the tone
3. Update page structures to add compact summary/hero sections
4. Consolidate form, empty-state, and feedback styles
5. Add minimal JS changes only where needed for quick actions or retry triggers

## Success Criteria

The refresh is successful if:

- All main pages look like one coherent product
- The app feels lighter, fresher, and more recognizable as a campus tool
- Send-page device selection is easier to understand at a glance
- Empty and error states provide clearer next steps
- The work stays small enough to be implemented without backend changes or a large refactor
