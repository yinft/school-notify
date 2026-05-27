# Table Action Link Buttons Design

## Goal

Fix low-contrast action buttons in admin tables by relying more on Element Plus native button variants and less on custom CSS.

## Scope

- Update table action buttons on the admin list pages.
- Keep existing actions, icons, and button types.
- Do not change backend behavior, page layout structure, or non-table buttons.

## Problem

Current table action buttons are mostly rendered with `text` buttons. In the current theme some of them appear too light against the table background. The versions table also adds custom button color overrides that diverge from the rest of the project and reduce consistency.

## Recommended Approach

Use Element Plus native `link` buttons for table action columns.

- Replace `text` with `link` in table action buttons.
- Keep semantic `type` values such as `primary`, `warning`, and `danger` so Element Plus handles the color system.
- Remove version-table-specific action button skinning from global CSS.
- Keep `.table-actions` and `.table-actions-wide` only for layout and spacing.

This is the smallest change that improves contrast while staying close to the component library defaults.

## Affected Areas

- `src/pages/versions/VersionsPage.vue`
- `src/pages/notifications/NotificationsPage.vue`
- `src/pages/users/UsersPage.vue`
- `src/pages/devices/DevicesPage.vue`
- `src/styles/main.css`

## Error Handling And Risk

This change is presentational only. Main risk is small spacing or wrapping differences because `link` buttons have slightly different default padding from `text` buttons. Existing `.table-actions` flex layout should absorb that without structural changes.

## Verification

- Confirm all table action buttons are visible and readable.
- Confirm semantic colors still match action intent.
- Run `npm run build` to verify the admin app still compiles.
