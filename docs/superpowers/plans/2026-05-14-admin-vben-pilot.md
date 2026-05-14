# Admin Vben Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a parallel `admin-vben/` frontend pilot with login, authenticated shell, fixed menu routes, and existing backend auth integration.

**Architecture:** Add a new standalone Vite + Vue 3 app under `admin-vben/` instead of replacing the current `admin/`. Reuse the existing backend auth contract and implement a lightweight vben-inspired shell with local route definitions, a Pinia auth store, an Axios client, and dev proxy-based `/api` requests.

**Tech Stack:** Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios, Element Plus

---

## File Structure

- Create: `admin-vben/package.json` - frontend package manifest and scripts
- Create: `admin-vben/tsconfig.json` - TypeScript config
- Create: `admin-vben/vite.config.ts` - Vite config with `/api` dev proxy
- Create: `admin-vben/index.html` - app entry HTML
- Create: `admin-vben/src/main.ts` - app bootstrap
- Create: `admin-vben/src/App.vue` - root app shell
- Create: `admin-vben/src/vite-env.d.ts` - Vite type declarations
- Create: `admin-vben/src/router/index.ts` - routes and auth guard
- Create: `admin-vben/src/stores/auth.ts` - token persistence and hydration logic
- Create: `admin-vben/src/services/http.ts` - Axios client and 401 handling
- Create: `admin-vben/src/services/adminAuth.ts` - login/me/logout API wrappers
- Create: `admin-vben/src/layouts/AdminShell.vue` - authenticated shell layout
- Create: `admin-vben/src/components/AppSidebar.vue` - left navigation
- Create: `admin-vben/src/components/AppHeader.vue` - top bar with logout
- Create: `admin-vben/src/pages/login/LoginPage.vue` - login UI
- Create: `admin-vben/src/pages/dashboard/DashboardPage.vue` - placeholder page
- Create: `admin-vben/src/pages/devices/DevicesPage.vue` - placeholder page
- Create: `admin-vben/src/pages/users/UsersPage.vue` - placeholder page
- Create: `admin-vben/src/pages/notifications/NotificationsPage.vue` - placeholder page
- Create: `admin-vben/src/pages/versions/VersionsPage.vue` - placeholder page
- Create: `admin-vben/src/styles/main.css` - global and shell styles

### Task 1: Scaffold The `admin-vben` App

**Files:**
- Create: `admin-vben/package.json`
- Create: `admin-vben/tsconfig.json`
- Create: `admin-vben/vite.config.ts`
- Create: `admin-vben/index.html`
- Create: `admin-vben/src/main.ts`
- Create: `admin-vben/src/App.vue`
- Create: `admin-vben/src/vite-env.d.ts`
- Create: `admin-vben/src/styles/main.css`

- [ ] **Step 1: Create the package manifest**

```json
{
  "name": "school-notify-admin-vben",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.11.0",
    "element-plus": "^2.11.1",
    "pinia": "^3.0.3",
    "vue": "^3.5.13",
    "vue-router": "^4.5.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.1",
    "typescript": "^5.9.3",
    "vite": "^7.1.7"
  }
}
```

- [ ] **Step 2: Create TypeScript and Vite config**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5175,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: Create the app entry files**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>School Notify Admin</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

```ts
/// <reference types="vite/client" />
```

```vue
<template>
  <RouterView />
</template>
```

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './styles/main.css'

createApp(App).use(createPinia()).use(router).use(ElementPlus).mount('#app')
```

- [ ] **Step 4: Add the base stylesheet**

```css
:root {
  color: #d7dde8;
  background: #0f172a;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
  min-width: 320px;
}

body {
  background:
    radial-gradient(circle at top, rgba(56, 189, 248, 0.12), transparent 28%),
    linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: #d7dde8;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input {
  font: inherit;
}
```

- [ ] **Step 5: Install dependencies**

Run: `npm install`
Expected: install completes successfully inside `admin-vben`

- [ ] **Step 6: Commit scaffold**

```bash
git add admin-vben/package.json admin-vben/tsconfig.json admin-vben/vite.config.ts admin-vben/index.html admin-vben/src/main.ts admin-vben/src/App.vue admin-vben/src/vite-env.d.ts admin-vben/src/styles/main.css
git commit -m "feat: scaffold admin vben pilot"
```

### Task 2: Implement Auth Services And Store

**Files:**
- Create: `admin-vben/src/services/http.ts`
- Create: `admin-vben/src/services/adminAuth.ts`
- Create: `admin-vben/src/stores/auth.ts`

- [ ] **Step 1: Create the HTTP client**

```ts
import axios, { AxiosError, type AxiosRequestConfig } from 'axios'

const TOKEN_KEY = 'school-notify-admin-vben-token'

type RequestOptions = {
  method?: AxiosRequestConfig['method']
  params?: Record<string, unknown>
  data?: unknown
  headers?: Record<string, string>
  auth?: boolean
}

const http = axios.create({
  baseURL: '',
  timeout: 15000
})

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

function getErrorDetail(data: unknown) {
  if (typeof data !== 'object' || data === null || !('detail' in data)) {
    return ''
  }

  const detail = data.detail
  return typeof detail === 'string' ? detail : ''
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  try {
    const token = options.auth === false ? '' : getToken()
    const response = await http.request<T>({
      url: path,
      method: options.method,
      params: options.params,
      data: options.data,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      validateStatus: () => true
    })

    if (response.status === 401 && options.auth !== false) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      throw new Error('登录已过期，请重新登录')
    }

    if (response.status === 204) {
      return undefined as T
    }

    if (response.status < 200 || response.status >= 300) {
      throw new Error(getErrorDetail(response.data) || 'request failed')
    }

    return response.data
  } catch (error) {
    if (error instanceof Error && !(error instanceof AxiosError)) {
      throw error
    }

    const axiosError = error as AxiosError<{ detail?: string }>
    throw new Error(axiosError.response?.data?.detail || axiosError.message || 'request failed')
  }
}

export { TOKEN_KEY }
```

- [ ] **Step 2: Create backend auth API wrappers**

```ts
import { request } from './http'

export type AdminSession = {
  username: string
  display_name: string
  session_token: string
}

export type AdminProfile = {
  username: string
  display_name: string
}

export function loginAdmin(payload: { username: string; password: string }) {
  return request<AdminSession>('/api/admin/auth/login', {
    method: 'POST',
    data: payload,
    auth: false
  })
}

export function getAdminProfile() {
  return request<AdminProfile>('/api/admin/auth/me')
}

export function logoutAdmin() {
  return request<void>('/api/admin/auth/logout', {
    method: 'POST'
  })
}
```

- [ ] **Step 3: Create the auth store**

```ts
import { defineStore } from 'pinia'

import { getAdminProfile, loginAdmin, logoutAdmin, type AdminProfile, type AdminSession } from '../services/adminAuth'
import { TOKEN_KEY } from '../services/http'

type AuthState = {
  sessionToken: string
  profile: AdminProfile | null
  hydrating: boolean
  hydrated: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    sessionToken: localStorage.getItem(TOKEN_KEY) || '',
    profile: null,
    hydrating: false,
    hydrated: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.sessionToken)
  },
  actions: {
    async login(username: string, password: string) {
      const session: AdminSession = await loginAdmin({ username, password })
      this.sessionToken = session.session_token
      this.profile = {
        username: session.username,
        display_name: session.display_name
      }
      this.hydrated = true
      localStorage.setItem(TOKEN_KEY, session.session_token)
    },
    async hydrate() {
      if (this.hydrated || this.hydrating) {
        return
      }

      if (!this.sessionToken) {
        this.hydrated = true
        return
      }

      this.hydrating = true
      try {
        this.profile = await getAdminProfile()
      } catch {
        this.clear()
      } finally {
        this.hydrating = false
        this.hydrated = true
      }
    },
    async logout() {
      if (this.sessionToken) {
        try {
          await logoutAdmin()
        } finally {
          this.clear()
        }
        return
      }

      this.clear()
    },
    clear() {
      this.sessionToken = ''
      this.profile = null
      this.hydrating = false
      this.hydrated = true
      localStorage.removeItem(TOKEN_KEY)
    }
  }
})
```

- [ ] **Step 4: Run the app build to verify service and store typing**

Run: `npm run build`
Expected: build completes or fails only due to missing router/layout files from later tasks

- [ ] **Step 5: Commit auth foundation**

```bash
git add admin-vben/src/services/http.ts admin-vben/src/services/adminAuth.ts admin-vben/src/stores/auth.ts
git commit -m "feat: add admin vben auth integration"
```

### Task 3: Add Router, Guard, And Protected Shell

**Files:**
- Create: `admin-vben/src/router/index.ts`
- Create: `admin-vben/src/layouts/AdminShell.vue`
- Create: `admin-vben/src/components/AppSidebar.vue`
- Create: `admin-vben/src/components/AppHeader.vue`

- [ ] **Step 1: Create the router with protected routes**

```ts
import { createRouter, createWebHistory } from 'vue-router'

import AdminShell from '../layouts/AdminShell.vue'
import { useAuthStore } from '../stores/auth'

const LoginPage = () => import('../pages/login/LoginPage.vue')
const DashboardPage = () => import('../pages/dashboard/DashboardPage.vue')
const DevicesPage = () => import('../pages/devices/DevicesPage.vue')
const UsersPage = () => import('../pages/users/UsersPage.vue')
const NotificationsPage = () => import('../pages/notifications/NotificationsPage.vue')
const VersionsPage = () => import('../pages/versions/VersionsPage.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { public: true }
    },
    {
      path: '/',
      component: AdminShell,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: DashboardPage },
        { path: 'devices', name: 'devices', component: DevicesPage },
        { path: 'users', name: 'users', component: UsersPage },
        { path: 'notifications', name: 'notifications', component: NotificationsPage },
        { path: 'versions', name: 'versions', component: VersionsPage }
      ]
    }
  ]
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await authStore.hydrate()

  if (to.meta.public) {
    if (to.path === '/login' && authStore.isAuthenticated) {
      return '/dashboard'
    }
    return true
  }

  if (!authStore.isAuthenticated) {
    return '/login'
  }

  return true
})

export default router
```

- [ ] **Step 2: Create the sidebar component**

```vue
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const items = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Devices', path: '/devices' },
  { label: 'Users', path: '/users' },
  { label: 'Notifications', path: '/notifications' },
  { label: 'Versions', path: '/versions' }
]

function navigate(path: string) {
  router.push(path)
}
</script>

<template>
  <aside class="app-sidebar">
    <div class="app-sidebar__brand">
      <div class="app-sidebar__logo">SN</div>
      <div>
        <div class="app-sidebar__title">School Notify</div>
        <div class="app-sidebar__subtitle">Admin Pilot</div>
      </div>
    </div>

    <nav class="app-sidebar__nav">
      <button
        v-for="item in items"
        :key="item.path"
        class="app-sidebar__link"
        :class="{ 'is-active': route.path === item.path }"
        type="button"
        @click="navigate(item.path)"
      >
        {{ item.label }}
      </button>
    </nav>
  </aside>
</template>
```

- [ ] **Step 3: Create the header component**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const displayName = computed(() => authStore.profile?.display_name || authStore.profile?.username || 'Admin')

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div>
      <div class="app-header__eyebrow">Management Console</div>
      <h1 class="app-header__title">Admin Pilot</h1>
    </div>

    <div class="app-header__actions">
      <div class="app-header__user">{{ displayName }}</div>
      <el-button type="primary" plain @click="handleLogout">退出登录</el-button>
    </div>
  </header>
</template>
```

- [ ] **Step 4: Create the authenticated shell layout**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from '../components/AppHeader.vue'
import AppSidebar from '../components/AppSidebar.vue'

const route = useRoute()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/devices': 'Devices',
    '/users': 'Users',
    '/notifications': 'Notifications',
    '/versions': 'Versions'
  }

  return map[route.path] || 'Admin'
})
</script>

<template>
  <div class="app-shell">
    <AppSidebar />

    <div class="app-shell__body">
      <AppHeader />

      <main class="app-shell__content">
        <div class="app-shell__page-meta">
          <div class="app-shell__page-label">Workspace</div>
          <h2 class="app-shell__page-title">{{ pageTitle }}</h2>
        </div>

        <RouterView />
      </main>
    </div>
  </div>
</template>
```

- [ ] **Step 5: Commit routing and shell**

```bash
git add admin-vben/src/router/index.ts admin-vben/src/layouts/AdminShell.vue admin-vben/src/components/AppSidebar.vue admin-vben/src/components/AppHeader.vue
git commit -m "feat: add admin vben shell layout"
```

### Task 4: Add Login And Placeholder Pages

**Files:**
- Create: `admin-vben/src/pages/login/LoginPage.vue`
- Create: `admin-vben/src/pages/dashboard/DashboardPage.vue`
- Create: `admin-vben/src/pages/devices/DevicesPage.vue`
- Create: `admin-vben/src/pages/users/UsersPage.vue`
- Create: `admin-vben/src/pages/notifications/NotificationsPage.vue`
- Create: `admin-vben/src/pages/versions/VersionsPage.vue`

- [ ] **Step 1: Create the login page**

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const submitting = ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  if (submitting.value) {
    return
  }

  errorMessage.value = ''
  submitting.value = true

  try {
    await authStore.login(form.username, form.password)
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-page__hero">
      <div class="login-page__badge">School Notify</div>
      <h1 class="login-page__title">Admin Pilot</h1>
      <p class="login-page__text">
        A vben-inspired console pilot wired to the current backend auth API.
      </p>
    </div>

    <div class="login-card">
      <div class="login-card__header">
        <h2>登录后台</h2>
        <p>使用现有管理员账号进入系统。</p>
      </div>

      <el-form label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            autocomplete="current-password"
            placeholder="请输入密码"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <p v-if="errorMessage" class="login-card__error">{{ errorMessage }}</p>

        <el-button class="login-card__submit" type="primary" :loading="submitting" @click="handleSubmit">
          登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Create a reusable placeholder page shape**

```vue
<template>
  <section class="placeholder-page">
    <div class="placeholder-page__card">
      <div class="placeholder-page__eyebrow">Pilot Section</div>
      <h3 class="placeholder-page__title">Dashboard</h3>
      <p class="placeholder-page__text">This route is connected and ready for future migration from the existing admin app.</p>
    </div>
  </section>
</template>
```

Use the same structure for each page with the title changed to `Devices`, `Users`, `Notifications`, and `Versions`.

- [ ] **Step 3: Commit pages**

```bash
git add admin-vben/src/pages/login/LoginPage.vue admin-vben/src/pages/dashboard/DashboardPage.vue admin-vben/src/pages/devices/DevicesPage.vue admin-vben/src/pages/users/UsersPage.vue admin-vben/src/pages/notifications/NotificationsPage.vue admin-vben/src/pages/versions/VersionsPage.vue
git commit -m "feat: add admin vben login and placeholder pages"
```

### Task 5: Finish Shell Styling And Verify End-To-End

**Files:**
- Modify: `admin-vben/src/styles/main.css`

- [ ] **Step 1: Expand the stylesheet for login and shell UI**

```css
.login-page {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 440px);
  min-height: 100vh;
  padding: 48px;
  gap: 48px;
  align-items: center;
}

.login-page__hero {
  max-width: 560px;
}

.login-page__badge,
.app-header__eyebrow,
.app-shell__page-label,
.placeholder-page__eyebrow {
  color: #7dd3fc;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.login-page__title {
  margin: 18px 0 16px;
  font-size: clamp(42px, 5vw, 64px);
  line-height: 1;
  color: #f8fafc;
}

.login-page__text {
  margin: 0;
  font-size: 18px;
  line-height: 1.7;
  color: #94a3b8;
}

.login-card,
.placeholder-page__card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.78);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(18px);
}

.login-card {
  padding: 32px;
}

.login-card__header h2,
.placeholder-page__title,
.app-shell__page-title,
.app-header__title {
  margin: 0;
  color: #f8fafc;
}

.login-card__header p,
.placeholder-page__text {
  color: #94a3b8;
}

.login-card__error {
  margin: 0 0 16px;
  color: #fca5a5;
}

.login-card__submit {
  width: 100%;
}

.app-shell {
  display: flex;
  min-height: 100vh;
}

.app-sidebar {
  width: 260px;
  padding: 24px 18px;
  border-right: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(2, 6, 23, 0.72);
}

.app-sidebar__brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 32px;
}

.app-sidebar__logo {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, #38bdf8, #6366f1);
  color: #f8fafc;
  font-weight: 800;
}

.app-sidebar__title {
  color: #f8fafc;
  font-weight: 700;
}

.app-sidebar__subtitle {
  color: #94a3b8;
  font-size: 13px;
}

.app-sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.app-sidebar__link {
  padding: 12px 14px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: #cbd5e1;
  text-align: left;
  cursor: pointer;
}

.app-sidebar__link:hover,
.app-sidebar__link.is-active {
  background: rgba(56, 189, 248, 0.16);
  color: #f8fafc;
}

.app-shell__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.app-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  padding: 28px 32px 0;
}

.app-header__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.app-header__user {
  color: #cbd5e1;
}

.app-shell__content {
  padding: 24px 32px 32px;
}

.app-shell__page-meta {
  margin-bottom: 18px;
}

.app-shell__page-title {
  margin-top: 8px;
  font-size: 32px;
}

.placeholder-page__card {
  padding: 28px;
}

.placeholder-page__text {
  margin-bottom: 0;
  line-height: 1.7;
}

@media (max-width: 960px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .app-shell {
    flex-direction: column;
  }

  .app-sidebar {
    width: auto;
    border-right: 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  }

  .app-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

- [ ] **Step 2: Run the production build**

Run: `npm run build`
Expected: Vite build succeeds for `admin-vben`

- [ ] **Step 3: Run a quick manual smoke checklist**

Run: `npm run dev`
Verify:
- `/login` renders
- valid login reaches `/dashboard`
- refresh on `/dashboard` keeps session via `/api/admin/auth/me`
- sidebar routes switch between placeholder pages
- logout returns to `/login`

- [ ] **Step 4: Commit the pilot UI**

```bash
git add admin-vben/src/styles/main.css
git commit -m "feat: finish admin vben pilot ui"
```
