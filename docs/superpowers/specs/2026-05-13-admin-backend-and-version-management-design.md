# Admin Backend And Version Management Design

## Goal

Add a standalone Vue 3 admin frontend for managing miniapp users, devices, notification records, and website client versions, while extending the existing FastAPI backend with a dedicated admin API and a website-facing version management capability.

## Current Context

- The repo already contains `backend` (FastAPI), `miniapp` (WeChat miniapp), `website` (Nuxt), and `windows-client`.
- The backend already persists `users`, `auth_sessions`, `devices`, `user_devices`, `notifications`, and `notification_deliveries`.
- The website currently has a downloads area and recent commits show device version content is already becoming part of the website flow.
- The backend already separates user-facing APIs and device-facing APIs well enough to extend with a dedicated admin surface.

## Chosen Direction

Use a new standalone `admin/` frontend project and keep all admin business logic inside the existing `backend` service.

This keeps the admin UI decoupled from the marketing website and the miniapp, while avoiding the cost of introducing a separate admin backend service.

## Scope

This design covers:

- A new standalone `admin/` Vue 3 project
- Dedicated admin authentication
- Admin dashboard
- Device management
- Miniapp user management
- Global notification record management
- Website client version management
- Public backend version APIs for the website
- Backend data model additions required by the admin features

This design does not cover:

- Multi-role or fine-grained admin permissions
- Device or user disable/freeze controls
- Notification retry in the first version
- Device-installed-version vs published-version comparison workflows
- Replacing the website with the admin frontend

## Architecture

The system will be split into four clear consumption surfaces:

- `miniapp`: normal end-user workflows
- `windows-client`: device registration, heartbeat, and realtime delivery
- `admin`: management console for operators
- `website`: public site for product presentation and downloads

The backend remains the single API service, but its routes are separated by consumer type:

- User-facing APIs remain under existing `/api/*` routes
- Device-facing APIs remain under existing `/api/*` and `/ws/*` routes
- Admin APIs live under `/api/admin/*`
- Public website version APIs live under `/api/public/versions/*`

This route split keeps deployment simple while making authorization, logging, and future middleware behavior easy to reason about.

## Admin Frontend

### Tech Stack

The new `admin/` project should use:

- Vue 3
- Vite
- Vue Router
- Pinia
- Element Plus

The goal is to feel similar to `vue3-admin` style projects without importing a heavy prebuilt admin framework.

### Project Structure

Suggested structure:

- `admin/src/main.ts`
- `admin/src/App.vue`
- `admin/src/router/`
- `admin/src/stores/`
- `admin/src/layouts/`
- `admin/src/pages/login/`
- `admin/src/pages/dashboard/`
- `admin/src/pages/devices/`
- `admin/src/pages/users/`
- `admin/src/pages/notifications/`
- `admin/src/pages/versions/`
- `admin/src/components/`
- `admin/src/services/`
- `admin/src/assets/`
- `admin/src/styles/`

### Branding

The admin UI should reuse the existing product icon and visual identity rather than inventing a separate brand.

The existing icon should be used in:

- Browser favicon
- Login page brand area
- Sidebar logo area

The admin visual style should be clean and product-like, not a generic template dump and not a marketing-style landing page.

### Layout

Use a classic admin shell:

- Left sidebar with logo and menu
- Top bar with breadcrumb and current admin actions
- Main content area for filters, charts, tables, and drawers/dialogs

Menu items for the first version:

- Dashboard
- Devices
- Users
- Notifications
- Versions

### Pages

#### Login

The login page contains:

- Brand area with icon and product name
- Simple admin login form with username and password

#### Dashboard

The dashboard should include:

- Summary cards for total devices, online devices, total users, and total notifications
- A notification trend chart for the last 7 days
- An online vs offline device ratio chart
- A client version distribution chart
- A small recent versions panel

The dashboard should be visually richer than a plain table page, but remain lightweight and fast.

#### Devices

The device page should provide:

- Search and filters by device ID, device name, online status, and client version
- Paginated full-device list
- Device detail drawer or page
- Editing for `device_name` and `location_label`
- Unbind action for a device-user relationship

The first version should not allow physical device deletion.

#### Users

The user page should provide:

- Search and filters by `user_id` and nickname
- Paginated user list
- User detail drawer or page
- Bound device view
- Recent notification view for the selected user

The first version is focused on inspection and relationship visibility rather than punitive operations.

#### Notifications

The notifications page should provide:

- Global notification search
- Filters by sender user, device, title keyword, time range, and delivery status
- Notification list with aggregate delivery counts
- Notification detail with delivery records

The first version does not include retry/replay actions.

#### Versions

The version page should provide:

- Version list and search
- Create version record
- Edit version record
- Delete unpublished version record
- Publish or unpublish version record
- Mark one published version as recommended per platform

This module is the admin surface for website download/version management.

## Backend Route Design

### Admin Auth

- `POST /api/admin/auth/login`
- `POST /api/admin/auth/logout`
- `GET /api/admin/auth/me`

Admin authentication must be fully separate from miniapp user authentication.

### Admin Dashboard

- `GET /api/admin/dashboard/summary`

This endpoint returns the cards and charts required by the dashboard page.

### Admin Devices

- `GET /api/admin/devices`
- `GET /api/admin/devices/{device_id}`
- `PATCH /api/admin/devices/{device_id}`
- `DELETE /api/admin/devices/{device_id}/bindings/{user_id}`

### Admin Users

- `GET /api/admin/users`
- `GET /api/admin/users/{user_id}`

User detail can include bound devices and recent notifications in one response for the first version.

### Admin Notifications

- `GET /api/admin/notifications`
- `GET /api/admin/notifications/{notification_id}`

### Admin Versions

- `GET /api/admin/versions`
- `GET /api/admin/versions/{id}`
- `POST /api/admin/versions`
- `PATCH /api/admin/versions/{id}`
- `DELETE /api/admin/versions/{id}`
- `POST /api/admin/versions/{id}/publish`
- `POST /api/admin/versions/{id}/unpublish`
- `POST /api/admin/versions/{id}/recommend`

### Public Website Versions

- `GET /api/public/versions`
- `GET /api/public/versions/recommended`

Public responses must expose only website-safe fields and only published versions.

## Backend Data Model

### New Tables

#### `admin_users`

Fields:

- `id`
- `username`
- `password_hash`
- `display_name`
- `is_active`
- `last_login_at`
- `created_at`
- `updated_at`

Although the first version only needs one admin account, the table should support multiple admin accounts later.

#### `admin_sessions`

Fields:

- `id`
- `admin_user_id`
- `session_token`
- `expires_at`
- `created_at`
- `last_seen_at`

This keeps admin sessions fully separate from end-user sessions.

#### `client_versions`

Fields:

- `id`
- `platform`
- `version`
- `build_number`
- `release_notes`
- `download_url`
- `file_size`
- `is_published`
- `is_recommended`
- `published_at`
- `created_by`
- `created_at`
- `updated_at`

Even if the first version only manages the Windows client, `platform` should be included so the schema does not need rework later.

### Existing Tables

No user or device disable flags are added in the first version.

The first version should keep current device and user lifecycle semantics simple:

- Unbinding deletes the `user_devices` relationship row
- Devices are not physically deleted from the admin UI
- Notifications remain queryable from existing notification tables

Additional fields should only be added if implementation reveals a concrete gap, not as speculative expansion.

## Version Management Rules

The following rules are fixed for the first version:

- New version records start unpublished
- Unpublished versions can be edited and deleted
- Published versions can still update release notes and download URL
- Published versions cannot change their version identifier
- Only published versions can become recommended
- Only one recommended version is allowed per platform
- Unpublished or unpublished-again versions do not appear in public website APIs

These rules keep the website behavior stable while still allowing operational correction of release notes and download links.

## Backend Code Organization

The current backend structure should be extended rather than replaced.

Suggested new route files:

- `backend/src/app/api/routes/admin_auth.py`
- `backend/src/app/api/routes/admin_dashboard.py`
- `backend/src/app/api/routes/admin_devices.py`
- `backend/src/app/api/routes/admin_users.py`
- `backend/src/app/api/routes/admin_notifications.py`
- `backend/src/app/api/routes/admin_versions.py`
- `backend/src/app/api/routes/public_versions.py`

Suggested new schema files:

- `backend/src/app/schemas/admin_auth.py`
- `backend/src/app/schemas/admin_dashboard.py`
- `backend/src/app/schemas/admin_device.py`
- `backend/src/app/schemas/admin_user.py`
- `backend/src/app/schemas/admin_notification.py`
- `backend/src/app/schemas/admin_version.py`

Suggested new service files:

- `backend/src/app/services/admin_auth.py`
- `backend/src/app/services/admin_dashboard.py`
- `backend/src/app/services/admin_queries.py`
- `backend/src/app/services/admin_versions.py`

The admin query logic should not be pushed into the existing main `store.py` more than necessary. The store can still be reused for shared low-level operations, but admin-specific filtering, pagination, and aggregation should live in admin-oriented services.

## Authorization Model

The backend should maintain three clear auth modes:

- End-user auth for miniapp flows
- Device auth/connection state for client flows
- Admin auth for `/api/admin/*`

Dedicated admin dependencies such as `require_current_admin` should be introduced rather than reusing end-user auth checks.

Public version endpoints should be anonymous read-only APIs.

## Website Integration

The website should stop relying on hardcoded version metadata for download presentation once the version APIs are available.

It should instead fetch published version data from the backend public version endpoints.

The website should only render fields that are intended for public display, such as:

- `platform`
- `version`
- `release_notes`
- `download_url`
- `file_size`
- `published_at`

## Deployment Model

- `admin/` is built and deployed as a static frontend
- `backend` remains the single API server
- `admin` calls the backend over HTTP under the admin route group
- `website` calls the backend over HTTP for public version data

This matches the existing repository and service layout while keeping the admin deployable independently from the website UI bundle.

## Testing Expectations

The implementation should include:

- Backend tests for admin auth behavior
- Backend tests for version management rules
- Backend tests for public version filtering
- Backend tests for admin device, user, and notification list/detail endpoints
- Frontend smoke-level tests where already practical in the repo setup

At minimum, the backend behavior around session isolation and version publish/recommend rules should be covered before considering the feature complete.

## Implementation Order

Recommended order:

1. Add admin auth tables, models, services, routes, and tests
2. Add client version table, routes, public APIs, and tests
3. Update the website to consume public version APIs
4. Scaffold the standalone `admin/` app with branding, routing, login, and shell layout
5. Implement the admin version management page first
6. Implement admin dashboard APIs and page
7. Implement admin devices, users, and notifications APIs and pages

This order creates an early working slice with immediate value for website version management before the larger management UI is completed.

## Risks And Constraints

- Admin query complexity can bloat the current backend service layer if the separation is not maintained
- Redis-backed online state should be queried carefully for dashboard statistics to avoid wasteful aggregation patterns
- Existing website download content may need a short compatibility phase during the switch to version-table-driven data
- Notification retry is intentionally excluded from the first version because it changes delivery semantics and audit expectations

## Summary

The first version should be a focused management console, not a fully generalized operations platform.

The design intentionally keeps the scope tight:

- standalone admin frontend
- dedicated admin auth
- rich enough dashboard
- operational visibility over devices, users, and notifications
- full website version record management
- public version APIs for the website

That delivers the requested management capability without prematurely introducing roles, disable flows, retry semantics, or a second backend service.
