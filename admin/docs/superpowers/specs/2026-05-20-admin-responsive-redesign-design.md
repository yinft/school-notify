# Admin Responsive Redesign Design

## Goal

Make the admin project usable on small screens, prevent table content from overflowing cards, align table content consistently, and upgrade the interface from a plain Element Plus assembly to a cohesive light blue-green admin console.

## Scope

- Keep Vue 3, Vite, TypeScript, Pinia, Vue Router, ECharts, and Element Plus.
- Do not add a new UI library or change backend APIs.
- Update the admin shell, dashboard cards/charts, list page filters, table containers, table cell alignment, drawer/dialog responsiveness, and login visual consistency.
- Preserve existing business logic and routes.

## Responsive Layout

The desktop layout keeps a left sidebar and topbar. At tablet widths the shell becomes a single-column layout with the sidebar acting as a compact horizontal navigation area. At phone widths the content padding, topbar actions, filters, cards, drawers, dialogs, and pagination collapse into single-column or horizontally scrollable patterns.

List tables use a shared `.table-scroll` wrapper. Tables keep readable minimum widths and scroll horizontally inside their cards instead of compressing columns until content breaks the layout.

## Table Rules

- IDs, URLs, release notes, and titles use tooltip or safe word breaking.
- Operation columns use a wrapping `.table-actions` group.
- Table cells align vertically in the middle.
- Header, hover, stripe, and row status styles are centralized in global CSS.

## Visual Direction

Use a clean technology-console style: soft gradient page background, white translucent cards, blue-cyan primary accents, refined shadows, stronger active navigation, polished form controls, and calmer dashboard charts. The design stays light and operationally readable.

## Verification

- Static regression test checks all list pages use `.table-scroll`, table action groups, and responsive CSS classes/media queries exist.
- `npm run build` verifies Vue and TypeScript compile successfully.
