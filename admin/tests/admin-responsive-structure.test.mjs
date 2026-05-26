import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(fileURLToPath(new URL('..', import.meta.url)))

function read(relativePath) {
  return readFileSync(resolve(root, relativePath), 'utf8')
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

const listPages = [
  'src/pages/devices/DevicesPage.vue',
  'src/pages/users/UsersPage.vue',
  'src/pages/notifications/NotificationsPage.vue',
  'src/pages/versions/VersionsPage.vue'
]

for (const page of listPages) {
  const source = read(page)
  assert(source.includes('class="table-scroll"'), `${page} must wrap el-table in .table-scroll`)
  assert(/class="[^"]*table-actions[^"]*"/.test(source), `${page} must wrap operation buttons in .table-actions`)
}

const css = read('src/styles/main.css')
const dashboard = read('src/pages/dashboard/DashboardPage.vue')
const layout = read('src/layouts/AdminLayout.vue')
for (const selector of ['.table-scroll', '.table-actions', '.responsive-shell-glow', '.mobile-nav-hint']) {
  assert(css.includes(selector), `main.css must include ${selector}`)
}

for (const query of ['@media (max-width: 1100px)', '@media (max-width: 720px)', '@media (max-width: 520px)']) {
  assert(css.includes(query), `main.css must include ${query}`)
}

assert(css.includes('--filter-search-width'), 'main.css must define --filter-search-width for compact filters')
assert(css.includes('grid-template-columns: minmax(220px, var(--filter-search-width)) auto'), 'single filter rows must not stretch across the whole screen')
assert(css.includes('.admin-shell {\n  position: relative;\n  grid-template-columns: 270px minmax(0, 1fr);\n  grid-template-rows: 1fr;'), 'desktop admin shell must keep sidebar and main in one full-height row')
assert(css.includes('height: 100dvh'), 'admin shell must use viewport height that supports internal scrolling')
assert(css.includes('overscroll-behavior: contain'), 'admin content must keep dashboard scrolling inside the main pane')
assert(css.includes('.dashboard-page'), 'main.css must include dashboard-specific fit layout')
assert(!css.includes('grid-template-rows: minmax(116px, 0.8fr)'), 'dashboard must not force metric cards into fixed-height content bands')
assert(dashboard.includes('<el-row class="analysis-overview-grid"'), 'dashboard metric cards must use Element Plus row grid')
assert(dashboard.includes(':xs="24"'), 'dashboard grids must collapse to one column on extra-small screens')
assert(dashboard.includes(':sm="12"'), 'dashboard grids must use two columns on small screens')
assert(dashboard.includes(':lg="6"'), 'dashboard metric cards must use four columns on large screens')
assert(dashboard.includes(':lg="8"'), 'dashboard chart cards must use three columns on large screens')
assert(css.includes('min-height: 0'), 'dashboard fit layout must allow grid children to shrink')
assert(dashboard.includes('Monitor'), 'dashboard device card must use a semantic device icon')
assert(dashboard.includes('Connection'), 'dashboard online card must use a semantic connection icon')
assert(dashboard.includes('UserFilled'), 'dashboard user card must use a semantic user icon')
assert(dashboard.includes('BellFilled'), 'dashboard notification card must use a semantic notification icon')
assert(dashboard.includes('metric-card-illustration'), 'dashboard cards must render SVG illustrations')
assert(css.includes('.metric-card-illustration'), 'main.css must style dashboard SVG illustrations')
assert(dashboard.includes('trendDays'), 'dashboard must track selected trend day range')
assert(dashboard.includes('fetchDashboardNotificationTrend({ days: trendDays.value })'), 'dashboard must refresh only notification trend when day range changes')
assert(!dashboard.includes('fetchDashboardSummary({ trend_days: trendDays.value })'), 'dashboard must not reload full summary when day range changes')
assert(dashboard.includes('const summaryLoading = ref(false)'), 'dashboard must separate initial summary loading state')
assert(dashboard.includes('const trendLoading = ref(false)'), 'dashboard must separate notification trend loading state')
assert(dashboard.includes('v-loading="summaryLoading"'), 'non-trend dashboard cards must only use summaryLoading')
assert(dashboard.includes('v-loading="trendLoading"'), 'notification trend card must only use trendLoading')
assert(dashboard.includes('async function renderTrendChart()'), 'trend range changes must render only the trend chart')
assert(dashboard.includes('await renderTrendChart()'), 'trend reload must not re-render every chart')
assert(dashboard.includes(':class="{ active: trendDays === 30 }"'), 'dashboard must expose a 30-day trend toggle')
assert(css.includes('/* Liquid glass pure-color overrides */'), 'main.css must include liquid glass pure-color overrides')
assert(css.includes('background: #f4f7fb;'), 'liquid glass theme must use a pure page background color')
assert(css.includes('background: rgb(255 255 255 / 72%);'), 'liquid glass cards must use translucent pure white')
assert(css.includes('--el-color-primary: #2563eb;'), 'Element Plus primary color must be a solid pure color')
assert(css.includes('background-color: #2563eb;'), 'primary buttons must use solid background-color')
assert(css.includes('background-image: none !important;'), 'primary buttons must not use gradient backgrounds')
assert(layout.includes('<el-menu'), 'sidebar navigation should use Element Plus el-menu')
assert(layout.includes('<el-menu-item'), 'sidebar navigation should use Element Plus el-menu-item')
assert(!layout.includes('class="nav-link"'), 'sidebar navigation should not use custom nav-link router styling')
assert(css.includes('/* Final pure-color Element Plus shell overrides */'), 'main.css must include final pure-color Element Plus shell overrides')
assert(css.includes('.admin-sidebar .el-menu-item.is-active'), 'sidebar active state must be driven by Element Plus menu item styling')
assert(css.includes('.brand-block {\n  background: #ffffff;'), 'brand block must use pure color background')

console.log('Admin responsive structure checks passed')
