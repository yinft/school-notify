# Admin Vben Pilot Design

## Goal

Create a parallel `admin-vben/` frontend pilot that adopts a `vue-vben-admin`-style admin shell while integrating with the existing backend admin authentication APIs. The pilot should prove the new frontend architecture by shipping login, authenticated layout, route guard, fixed menu, and placeholder pages without replacing the current `admin/` app yet.

## Scope

In scope:
- Add a new standalone frontend project under `admin-vben/`
- Use a Vite-based Vue 3 app with a `vue-vben-admin`-inspired layout and interaction model
- Integrate existing backend auth APIs:
  - `POST /api/admin/auth/login`
  - `GET /api/admin/auth/me`
  - `POST /api/admin/auth/logout`
- Add token persistence, auth hydration, route guard, logout flow, and fixed navigation
- Add placeholder pages for `dashboard`, `devices`, `users`, `notifications`, and `versions`
- Add local dev proxy for `/api`

Out of scope:
- Replacing the existing `admin/` project
- Migrating existing business pages into the new app
- Dynamic menu generation from backend data
- Permission model changes
- Backend API changes

## Current Context

The current `admin/` app is a lightweight Vue 3 + Pinia + Element Plus Vite project with direct page implementations for login, dashboard, devices, users, notifications, and versions. Backend admin auth already exists and returns a bearer token in the login response. The current backend does not need API changes for this pilot.

The upstream `vue-vben-admin` repository is a much heavier monorepo and would be expensive to import wholesale for a small pilot. For this reason, the pilot should borrow the architectural shape and UX style rather than embedding the full upstream workspace.

## Approaches Considered

### Approach 1: Parallel lightweight `admin-vben/` pilot

Create a new isolated frontend app that mirrors the core admin shell patterns of `vue-vben-admin` while keeping the project structure small and easy to adapt to this repository.

Pros:
- Lowest integration risk
- Does not disrupt the working `admin/` app
- Fastest path to validate backend auth integration and layout direction
- Easy to compare old and new apps side by side

Cons:
- Not a byte-for-byte import of the upstream project
- Some shell behavior is implemented locally instead of inherited from upstream

### Approach 2: Import a full `vue-vben-admin` app into the repo

Bring in one of the official web app packages and adapt it to the backend.

Pros:
- Maximum alignment with upstream conventions
- Easier future adoption of upstream features

Cons:
- Much higher setup cost
- Requires workspace and tooling changes that are disproportionate to the pilot scope
- Harder to reason about and maintain during initial integration

### Approach 3: Restyle the existing `admin/` app in place

Keep the current project and only change layout and styling toward a vben-like look.

Pros:
- Smallest code move
- Reuses existing page code directly

Cons:
- Does not provide a clean pilot boundary
- Harder to evaluate a future replacement path
- Leaves current project structure constraints in place

### Recommendation

Use Approach 1. It provides a clean migration path, contains risk, and proves the backend integration with the smallest irreversible change.

## Architecture

### Project Boundary

Add a new `admin-vben/` directory as a separate frontend application with its own `package.json`, Vite config, source tree, and build output. It will live alongside the current `admin/` app.

The existing `admin/` app remains untouched as the stable implementation while the pilot is evaluated.

### App Structure

The new app should be organized around a few focused units:
- `src/main.ts`: app bootstrap
- `src/router/`: route definitions and auth guard
- `src/stores/`: auth state and session hydration
- `src/services/`: HTTP client and backend auth API wrappers
- `src/layouts/`: authenticated admin shell
- `src/pages/login/`: login page
- `src/pages/*`: placeholder pages for each menu section
- `src/components/`: shell components such as sidebar, header, or menu wrappers if needed
- `src/styles/`: global and theme styles

This keeps the code easy to extend when real pages migrate later.

### UI Direction

The pilot should emulate the `vue-vben-admin` feel rather than duplicate every upstream implementation detail. The shell should include:
- A dark left sidebar with app branding and menu items
- A top header showing current admin identity and logout action
- A content area with page title and placeholder card/body
- A login page styled closer to a modern admin product than the current basic form

The menu structure should be fixed and local for the pilot:
- Dashboard
- Devices
- Users
- Notifications
- Versions

## Data Flow

### Login Flow

1. User opens `/login`
2. User submits username and password
3. Frontend calls `POST /api/admin/auth/login`
4. On success, store `session_token` in local storage and auth store
5. Populate profile from login response
6. Redirect to the default authenticated route, `/dashboard`

### Session Hydration Flow

1. App boots
2. Auth store reads token from local storage
3. If token exists, call `GET /api/admin/auth/me`
4. On success, hydrate profile and keep session
5. On failure, clear local session and force `/login`

### Logout Flow

1. User clicks logout in header
2. Frontend calls `POST /api/admin/auth/logout`
3. Regardless of API result, clear local session state
4. Redirect to `/login`

### Request Flow

The HTTP client should send requests to relative `/api/...` paths. Development uses a Vite proxy, and production is expected to use same-domain Nginx reverse proxying.

Authenticated requests should attach:
- `Authorization: Bearer <session_token>`

If a protected request returns `401`, the client should clear session state and redirect to `/login`.

## Routing And Navigation

Routes should be split into:
- Public route: `/login`
- Protected routes under a shared shell layout

Protected child routes:
- `/dashboard`
- `/devices`
- `/users`
- `/notifications`
- `/versions`

The route guard should:
- Redirect unauthenticated access to `/login`
- Redirect authenticated visits to `/login` back to `/dashboard`
- Avoid rendering protected pages before session hydration is resolved

The pilot may use a simple boot-time loading state while hydration completes.

## Error Handling

The pilot should keep error handling minimal and explicit:
- Invalid login credentials show a clear inline or toast error
- Failed `me` request clears stale token and returns user to login
- Logout clears local state even if backend logout fails
- Request timeout or network error shows a generic user-facing message

The pilot should not add retry queues, refresh tokens, or background re-auth logic.

## Tooling And Dependencies

The pilot should stay lightweight and close to the current stack unless a package is clearly needed.

Expected baseline:
- Vue 3
- Vue Router
- Pinia
- Vite
- Axios
- A UI layer appropriate for a vben-like shell, likely one of:
  - keep Element Plus for speed and compatibility, or
  - use lightweight custom shell styling plus only a few UI components

For the pilot, prefer the smaller option that achieves the visual goal without pulling in the full upstream monorepo dependency graph.

## Testing And Verification

Minimum verification for the pilot:
- Build the new `admin-vben/` app successfully
- Verify login flow against the existing backend
- Verify refresh with valid token stays authenticated
- Verify invalid or missing token redirects to login
- Verify logout clears session and returns to login
- Verify all fixed menu routes render their placeholder pages inside the shell

If practical, add at least lightweight automated coverage around auth store or route guard behavior. The initial pilot can otherwise rely on build verification and manual auth flow validation if the test setup cost would overwhelm the pilot scope.

## Deployment Expectation

The pilot should follow the same deployment assumption as the updated `admin/` app:
- Development: Vite dev server proxies `/api` to `http://127.0.0.1:8000`
- Production: frontend and backend share the same domain, and Nginx proxies `/api` to the backend service

No `VITE_API_BASE_URL` support is required for this pilot.

## Success Criteria

The pilot is successful when:
- `admin-vben/` runs independently from the existing `admin/`
- A user can log in with the existing backend admin account
- The authenticated shell renders with fixed sidebar and header navigation
- Refresh preserves the authenticated state via `/api/admin/auth/me`
- Logout works and returns to login
- Placeholder pages exist for the five target sections
- The project builds successfully

## Risks And Mitigations

### Risk: Over-importing upstream complexity

Mitigation:
- Keep the pilot as a standalone lightweight app
- Reuse only the shell ideas and interaction model required for the pilot

### Risk: Visual mismatch with expected vben feel

Mitigation:
- Focus first on matching layout hierarchy and core interaction patterns
- Treat this pilot as a validation step before migrating business pages

### Risk: Auth integration edge cases differ from the current app

Mitigation:
- Reuse the current backend contract exactly
- Keep token storage, hydration, and 401 handling behavior aligned with the current admin logic
