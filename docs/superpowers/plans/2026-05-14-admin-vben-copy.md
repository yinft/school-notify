# Admin Vben Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the existing `admin/` Vue app so login, shell, dashboard, and shared page chrome closely copy the desktop `vue-vben-admin` project while keeping Element Plus and existing backend data flow.

**Architecture:** Modify the current app in place. Recreate the Vben authentication layout, light design tokens, analysis overview cards, and chart cards with local Vue templates and CSS instead of importing Vben monorepo packages.

**Tech Stack:** Vue 3, TypeScript, Vue Router, Pinia, Axios, Element Plus, ECharts, Vite

---

## File Structure

- Modify: `admin/src/pages/login/LoginPage.vue` - Vben-like authentication layout using Element Plus form controls.
- Modify: `admin/src/layouts/AdminLayout.vue` - Vben-like light admin shell and menu structure.
- Modify: `admin/src/pages/dashboard/DashboardPage.vue` - Vben analysis overview and chart-card structure using current live summary data.
- Modify: `admin/src/styles/main.css` - Vben light tokens, copied layout/card/form/table utilities, and responsive behavior for all admin pages.

### Task 1: Copy Vben Design Tokens And Shared Styles

**Files:**
- Modify: `admin/src/styles/main.css`

- [ ] **Step 1: Replace global tokens and shell/card styles**

Replace the current file with a Vben-token stylesheet that preserves existing class names. The stylesheet must include `--background`, `--background-deep`, `--foreground`, `--card`, `--border`, `--primary`, `--muted-foreground`, `.card-box`, `.admin-shell`, `.admin-sidebar`, `.admin-topbar`, `.hero-panel`, `.table-card`, `.chart-card`, `.metric-card`, `.login-shell`, and the existing table/detail/status helper classes used by other pages.

- [ ] **Step 2: Verify no public class regressions**

Run: `npm run build`
Working directory: `admin`
Expected: TypeScript and Vite build complete successfully.

### Task 2: Copy Vben Login Layout

**Files:**
- Modify: `admin/src/pages/login/LoginPage.vue`
- Modify: `admin/src/styles/main.css`

- [ ] **Step 1: Rewrite login template around Vben authentication layout**

Use this structure:

```vue
<template>
  <div class="login-shell">
    <div class="login-logo-row">
      <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
      <p>思故桌面小喇叭</p>
    </div>

    <section class="login-intro-panel">
      <div class="login-background"></div>
      <div class="login-slogan-card enter-x">
        <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
        <h1>思故桌面小喇叭管理后台</h1>
        <p>统一查看设备、用户、通知和官网版本。</p>
      </div>
    </section>

    <section class="login-form-panel">
      <div class="login-card auth-form-view" @keydown.enter.prevent="handleSubmit">
        <div class="auth-title">
          <h2>欢迎回来 👋🏻</h2>
          <span>请输入管理员账号登录运营后台</span>
        </div>
        <el-form label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" size="large" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password autocomplete="current-password" size="large" placeholder="请输入密码" />
          </el-form-item>
          <div class="auth-extra-row">
            <span>会话失效后会自动返回登录页</span>
            <span class="vben-link">管理员登录</span>
          </div>
          <el-button class="auth-submit-button" type="primary" size="large" :loading="loading" @click="handleSubmit">
            登录
          </el-button>
        </el-form>
      </div>
    </section>
  </div>
</template>
```

- [ ] **Step 2: Keep login behavior unchanged**

Keep the existing `<script setup>` login logic: `form`, `loading`, `handleSubmit()`, `authStore.login()`, redirect to `/dashboard`, and `ElMessage.error()`.

- [ ] **Step 3: Build check**

Run: `npm run build`
Working directory: `admin`
Expected: build succeeds.

### Task 3: Copy Vben Admin Shell

**Files:**
- Modify: `admin/src/layouts/AdminLayout.vue`
- Modify: `admin/src/styles/main.css`

- [ ] **Step 1: Update shell template class names**

Keep the existing script and routes, but change the template to use Vben-like shell blocks:

```vue
<template>
  <div class="admin-shell">
    <aside class="admin-sidebar card-box">
      <div class="brand-block">
        <img src="/app-icon.png" alt="思故桌面小喇叭图标" />
        <div>
          <strong>思故桌面小喇叭</strong>
          <span>School Notify Admin</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <RouterLink v-for="item in menuItems" :key="item.path" :to="item.path" class="nav-link" :class="{ active: route.path === item.path }">
          <span class="nav-dot"></span>
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar card-box">
        <div>
          <p class="topbar-eyebrow">School Notify Admin</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="topbar-actions">
          <div class="admin-chip">
            <span>{{ authStore.profile?.display_name || '管理员' }}</span>
          </div>
          <el-button plain @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <section class="admin-content">
        <RouterView />
      </section>
    </main>
  </div>
</template>
```

- [ ] **Step 2: Build check**

Run: `npm run build`
Working directory: `admin`
Expected: build succeeds.

### Task 4: Copy Vben Dashboard Analysis Layout

**Files:**
- Modify: `admin/src/pages/dashboard/DashboardPage.vue`
- Modify: `admin/src/styles/main.css`

- [ ] **Step 1: Update card data for Vben overview footer rows**

Change the `cards` computed values to include `totalTitle` and `totalValue` fields:

```ts
return [
  { label: '设备总数', value: value.device_count, totalTitle: '在线设备', totalValue: value.online_device_count, tone: 'blue' },
  { label: '在线设备', value: value.online_device_count, totalTitle: '离线设备', totalValue: value.device_status_ratio.offline, tone: 'green' },
  { label: '用户总数', value: value.user_count, totalTitle: '通知记录', totalValue: value.notification_count, tone: 'amber' },
  { label: '通知记录', value: value.notification_count, totalTitle: '最近趋势', totalValue: value.notification_trend.reduce((sum, item) => sum + item.count, 0), tone: 'violet' }
]
```

- [ ] **Step 2: Update dashboard template**

Use Vben analysis structure:

```vue
<template>
  <div class="page-stack dashboard-page">
    <section v-if="errorMessage" class="feedback-banner error-banner standalone-banner card-box">
      <span>{{ errorMessage }}</span>
      <el-button text type="primary" @click="$router.go(0)">重试</el-button>
    </section>

    <section class="analysis-overview-grid">
      <article v-for="card in cards" :key="card.label" class="metric-card vben-card" :data-tone="card.tone" v-loading="loading">
        <header class="vben-card-header">
          <h3>{{ card.label }}</h3>
        </header>
        <div class="metric-card-content">
          <strong>{{ card.value }}</strong>
          <span class="metric-icon-dot"></span>
        </div>
        <footer class="metric-card-footer">
          <span>{{ card.totalTitle }}</span>
          <b>{{ card.totalValue }}</b>
        </footer>
      </article>
    </section>

    <section class="chart-tabs-card vben-card" v-loading="loading">
      <header class="vben-card-header chart-tabs-header">
        <h3>流量趋势</h3>
        <div class="chart-tab-pills">
          <span class="active">通知趋势</span>
          <span>最近 7 天</span>
        </div>
      </header>
      <div ref="trendChart" class="echart-canvas large-chart"></div>
    </section>

    <section class="chart-grid">
      <article class="chart-card vben-card" v-loading="loading">
        <header class="vben-card-header"><h3>在线设备占比</h3></header>
        <div ref="statusChart" class="echart-canvas"></div>
      </article>
      <article class="chart-card vben-card" v-loading="loading">
        <header class="vben-card-header"><h3>客户端版本分布</h3></header>
        <div ref="versionChart" class="echart-canvas"></div>
      </article>
      <article class="chart-card vben-card" v-loading="loading">
        <header class="vben-card-header"><h3>运营概览</h3></header>
        <div class="dashboard-summary-list">
          <div><span>设备在线率</span><strong>{{ summary ? `${Math.round((summary.device_status_ratio.online / Math.max(summary.device_count, 1)) * 100)}%` : '-' }}</strong></div>
          <div><span>用户总数</span><strong>{{ summary?.user_count ?? '-' }}</strong></div>
          <div><span>通知总量</span><strong>{{ summary?.notification_count ?? '-' }}</strong></div>
        </div>
      </article>
    </section>
  </div>
</template>
```

- [ ] **Step 3: Adjust ECharts colors to Vben tokens**

Use `#1677ff` as primary, `#52c41a` as success, `#d9d9d9` as muted border, and light split lines `rgba(5, 5, 5, 0.06)`.

- [ ] **Step 4: Build check**

Run: `npm run build`
Working directory: `admin`
Expected: build succeeds.

### Task 5: Final Verification

**Files:**
- Verify: `admin/src/pages/login/LoginPage.vue`
- Verify: `admin/src/layouts/AdminLayout.vue`
- Verify: `admin/src/pages/dashboard/DashboardPage.vue`
- Verify: `admin/src/styles/main.css`

- [ ] **Step 1: Run production build**

Run: `npm run build`
Working directory: `admin`
Expected: Vite reports build success and outputs `dist/` assets.

- [ ] **Step 2: Inspect git diff**

Run: `git diff -- admin/src/pages/login/LoginPage.vue admin/src/layouts/AdminLayout.vue admin/src/pages/dashboard/DashboardPage.vue admin/src/styles/main.css docs/superpowers/specs/2026-05-14-admin-vben-copy-design.md docs/superpowers/plans/2026-05-14-admin-vben-copy.md`
Expected: diff only contains the Vben copy restyle and plan/spec additions.

- [ ] **Step 3: Manual browser smoke check if dev server is available**

Run: `npm run dev`
Working directory: `admin`
Expected: Vite starts. Check `/login`, log in, check `/dashboard`, then click devices/users/notifications/versions to confirm shared layout is intact.

## Self-Review Notes

- Spec coverage: login, shell, dashboard, shared style, Element Plus constraint, and no backend changes are covered by Tasks 1-5.
- Placeholder scan: no implementation placeholders are required; each task names exact files and expected verification commands.
- Type consistency: dashboard card fields introduced in Task 4 are used by the template in the same task.
