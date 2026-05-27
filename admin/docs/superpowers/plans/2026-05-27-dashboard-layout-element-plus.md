# Dashboard Layout Element Plus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the dashboard trend section onto Element Plus page-level grid layout and make the trend chart readable on small screens with a scrollable chart viewport.

**Architecture:** Keep the dashboard's existing information hierarchy, but express every page-level region through `el-row` and `el-col`. Add a chart viewport wrapper inside the trend card so CSS handles horizontal scrolling and minimum width, while the existing ECharts logic only gets minimal small-screen label tuning.

**Tech Stack:** Vue 3, Element Plus, ECharts, Vite, Node-based structure checks

---

## File Map

- Modify: `tests/admin-responsive-structure.test.mjs`
  - Extend the existing UI structure checks to cover the new dashboard grid row and scrollable trend chart wrappers.
- Modify: `src/pages/dashboard/DashboardPage.vue`
  - Wrap the trend card in `el-row` and `el-col`.
  - Add the chart viewport and chart surface wrappers.
  - Apply small-screen ECharts x-axis label tuning without changing the existing data flow.
- Modify: `src/styles/main.css`
  - Add dashboard trend row and scroll-container styles.
  - Keep page-level layout in Element Plus and card-internal scrolling in CSS.

### Task 1: Lock the New Structure With a Failing Test

**Files:**
- Modify: `tests/admin-responsive-structure.test.mjs`
- Test: `tests/admin-responsive-structure.test.mjs`

- [ ] **Step 1: Write the failing test**

Add these assertions next to the existing dashboard structure checks:

```js
assert(dashboard.includes('<el-row class="trend-grid" :gutter="16">'), 'dashboard trend card must use an Element Plus row grid')
assert(dashboard.includes('<el-col :xs="24">'), 'dashboard trend row must span the full width on extra-small screens')
assert(dashboard.includes('class="trend-chart-viewport"'), 'dashboard trend card must include a scroll viewport wrapper')
assert(dashboard.includes('class="trend-chart-surface"'), 'dashboard trend card must include a min-width chart surface wrapper')
assert(css.includes('.dashboard-page .trend-grid'), 'main.css must include a dashboard trend grid rule')
assert(css.includes('.trend-chart-viewport'), 'main.css must include a trend chart viewport rule')
assert(css.includes('.trend-chart-surface'), 'main.css must include a trend chart surface rule')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:ui`

Expected: FAIL with a message like `dashboard trend card must use an Element Plus row grid` because the dashboard template and CSS do not yet contain those wrappers.

### Task 2: Move the Trend Card Onto the Element Plus Grid

**Files:**
- Modify: `src/pages/dashboard/DashboardPage.vue`
- Test: `tests/admin-responsive-structure.test.mjs`

- [ ] **Step 1: Write minimal implementation**

Replace the standalone trend section in `src/pages/dashboard/DashboardPage.vue` with this structure:

```vue
    <el-row class="trend-grid" :gutter="16">
      <el-col :xs="24">
        <section class="chart-tabs-card vben-card" v-loading="trendLoading">
          <header class="vben-card-header chart-tabs-header">
            <h3>流量趋势</h3>
            <div class="chart-tab-pills">
              <span class="active">通知趋势</span>
              <button type="button" :class="{ active: trendDays === 7 }" @click="setTrendDays(7)">最近 7 天</button>
              <button type="button" :class="{ active: trendDays === 30 }" @click="setTrendDays(30)">最近 30 天</button>
            </div>
          </header>
          <div class="trend-chart-viewport">
            <div class="trend-chart-surface">
              <div ref="trendChart" class="echart-canvas large-chart"></div>
            </div>
          </div>
        </section>
      </el-col>
    </el-row>
```

This is the only page-level template change needed.

- [ ] **Step 2: Run test to verify partial progress**

Run: `npm run test:ui`

Expected: FAIL, but now only on missing CSS selectors because the template wrappers exist and the stylesheet has not been updated yet.

### Task 3: Add the Small-Screen Scroll Container Styles

**Files:**
- Modify: `src/styles/main.css`
- Test: `tests/admin-responsive-structure.test.mjs`

- [ ] **Step 1: Write minimal implementation**

In the existing dashboard section of `src/styles/main.css`, make these changes:

```css
.dashboard-page .analysis-overview-grid,
.dashboard-page .trend-grid,
.dashboard-page .chart-grid {
  margin-right: 0 !important;
  margin-left: 0 !important;
  row-gap: 16px;
}

.dashboard-page .analysis-overview-grid > .el-col,
.dashboard-page .trend-grid > .el-col,
.dashboard-page .chart-grid > .el-col {
  display: flex;
  margin-bottom: 16px;
}

.dashboard-page .trend-grid > .el-col > .chart-tabs-card,
.dashboard-page .analysis-overview-grid > .el-col > .metric-card,
.dashboard-page .chart-grid > .el-col > .chart-card {
  width: 100%;
}

.dashboard-page .trend-chart-viewport {
  overflow-x: auto;
  overflow-y: hidden;
}

.dashboard-page .trend-chart-surface {
  min-width: 560px;
}

@media (max-width: 720px) {
  .dashboard-page .trend-chart-surface {
    min-width: 560px;
  }
}
```

Keep the existing `.chart-tabs-card .echart-canvas` spacing rule so the chart surface still uses the current card spacing.

- [ ] **Step 2: Run test to verify it passes**

Run: `npm run test:ui`

Expected: PASS with `Admin responsive structure checks passed`.

### Task 4: Tune the Trend Chart for Narrow Screens

**Files:**
- Modify: `src/pages/dashboard/DashboardPage.vue`
- Test: `tests/admin-responsive-structure.test.mjs`

- [ ] **Step 1: Write the failing test**

Add these assertions to `tests/admin-responsive-structure.test.mjs` after the existing trend chart checks:

```js
assert(dashboard.includes('const isTrendNarrow = window.innerWidth <= 720'), 'dashboard trend chart must detect narrow screens')
assert(dashboard.includes('interval: isTrendNarrow ? \'auto\' : 0'), 'dashboard trend chart must reduce label density on narrow screens')
assert(dashboard.includes('rotate: isTrendNarrow ? 30 : 0'), 'dashboard trend chart must rotate labels on narrow screens')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:ui`

Expected: FAIL because the current chart config always uses the same x-axis label settings.

- [ ] **Step 3: Write minimal implementation**

In `renderTrendChart()` inside `src/pages/dashboard/DashboardPage.vue`, add a narrow-screen flag and use it only for the x-axis label config:

```ts
  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    const isTrendNarrow = window.innerWidth <= 720

    chart.setOption({
      grid: { left: 24, right: 8, top: 20, bottom: isTrendNarrow ? 48 : 24 },
      xAxis: {
        type: 'category',
        data: notificationTrend.value.map((item) => item.date.slice(5)),
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: {
          color: '#71717a',
          interval: isTrendNarrow ? 'auto' : 0,
          rotate: isTrendNarrow ? 30 : 0
        }
      },
```

Do not change data fetching, loading state, or the rest of the chart behavior.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:ui`

Expected: PASS with `Admin responsive structure checks passed`.

### Task 5: Final Verification

**Files:**
- Modify: none
- Test: `tests/admin-responsive-structure.test.mjs`

- [ ] **Step 1: Run the structural UI check**

Run: `npm run test:ui`

Expected: PASS with `Admin responsive structure checks passed`.

- [ ] **Step 2: Run the production build**

Run: `npm run build`

Expected: PASS with Vite build output and no dashboard compile errors.

- [ ] **Step 3: Manual viewport verification**

Check the dashboard page in a browser at desktop width and at a narrow mobile width.

Confirm:

```text
1. The trend card sits inside its own Element Plus row/column.
2. The dashboard page does not gain horizontal page-level overflow.
3. The trend chart itself can scroll horizontally on narrow screens.
4. The 7-day and 30-day toggle still updates the chart.
5. The chart remains readable instead of being crushed.
```
