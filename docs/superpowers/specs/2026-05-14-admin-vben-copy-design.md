# Admin Vben Copy Design

## Goal

Restyle the current `admin/` management frontend so its login page, authenticated shell, dashboard, and shared public styles closely copy the desktop `vue-vben-admin` project, while keeping the existing Vue 3, Element Plus, Pinia, Router, Axios, and backend API integration.

## Scope

In scope:
- Update the existing `admin/` app in place.
- Copy the visible structure and styling cues from `vue-vben-admin` authentication layout, dashboard analysis cards, dashboard chart cards, and base design tokens.
- Keep Element Plus as the component library.
- Preserve current routes, stores, services, auth flow, and business data fetching.
- Let existing devices, users, notifications, and versions pages inherit the new shared Vben-like public styling without rewriting their business structure.

Out of scope:
- Importing the full `vue-vben-admin` monorepo or its internal packages.
- Replacing Element Plus with Vben shadcn components.
- Changing backend APIs or auth behavior.
- Adding dark mode, dynamic preferences, dynamic menus, permissions, or i18n.

## Reference Mapping

- Login layout copies `packages/effects/layouts/src/authentication/authentication.vue` and `packages/effects/common-ui/src/ui/authentication/login.vue` at the local DOM/CSS level.
- Dashboard metric cards copy `packages/effects/common-ui/src/ui/dashboard/analysis/analysis-overview.vue`.
- Dashboard chart cards copy `packages/effects/common-ui/src/ui/dashboard/analysis/analysis-chart-card.vue`.
- Global tokens copy the light theme values from `packages/@core/base/design/src/design-tokens/default.css`.

## Approach

Use a local manual copy rather than direct dependency integration. The upstream project relies on monorepo aliases, Tailwind utilities, shadcn components, preferences, and Vben form APIs. Pulling that dependency graph into this small admin app would be high risk. The local copy will reproduce the page structure, spacing, border, card, background, and token system with plain Vue templates, Element Plus components, and CSS.

## UI Design

### Login

The login page becomes a Vben authentication screen:
- Full-height two-column layout.
- App logo and app name at top left.
- Large background introduction area with Vben-style blurred `login-background` gradient.
- Floating brand/slogan block in the introduction area.
- Form panel matching the Vben login form hierarchy: title, subtitle, hidden-label inputs, remember/session hint row, full-width primary login button.
- Username/password submission remains unchanged.

### Authenticated Shell

The admin shell changes from the current dark glass sidebar to Vben's light token system:
- Body uses `hsl(var(--background-deep))`.
- Sidebar/header/cards use `hsl(var(--background))` and `hsl(var(--card))`.
- Borders use `hsl(var(--border))`.
- Primary color uses `hsl(var(--primary))`.
- Sidebar, header, and content spacing mirror Vben's clean admin shell density.
- Existing fixed menu items remain unchanged.

### Dashboard

Dashboard becomes a local copy of Vben's analysis layout:
- A four-column overview grid with card header, main value row, and footer summary row.
- The current live summary values remain the data source.
- Chart sections use Vben-style `Card`, `CardHeader`, `CardTitle`, and `CardContent` equivalents implemented with local markup and CSS.
- Existing ECharts charts remain, but their colors and grids are adjusted to the Vben token palette.

### Shared Styles

`admin/src/styles/main.css` becomes the central Vben token and utility layer for the current admin app:
- Replace glassmorphism gradients with Vben light tokens.
- Add local `.card-box`, `.vben-card`, `.vben-link`, and compatible page/card classes.
- Keep existing class names used by business pages so pages inherit the new appearance with minimal template churn.
- Preserve responsive behavior for tablet/mobile.

## Data Flow

No backend data flow changes. Login still calls the existing auth store. Dashboard still calls `fetchDashboardSummary()`. Business pages continue using their current services.

## Error Handling

Existing error behavior remains. Login failures still show `ElMessage.error`. Dashboard load failures still show an inline error banner with retry. The visual style of these states changes to match the copied Vben card/token system.

## Testing

Verification should include:
- `npm run build` inside `admin/`.
- Visual check of `/login`.
- Visual check of `/dashboard` with loaded and error/loading states where practical.
- Quick navigation check for devices, users, notifications, and versions to ensure shared style changes did not break layout.

## Success Criteria

- The current `admin/` app builds successfully.
- Login page visibly matches the Vben authentication layout rather than the previous custom design.
- Dashboard visibly matches Vben analysis card and chart-card layout.
- Shared admin cards, tables, filters, and layout use Vben light tokens and spacing.
- Element Plus remains the only UI component library used by this app.
