## Background

The admin dashboard page currently mixes Element Plus grid layout with a standalone trend section. The top metric cards and lower summary cards already use `el-row` and `el-col`, but the "流量趋势" card is rendered as a standalone section outside that page-level grid structure. On small screens, the trend chart shrinks with the container width, which makes the x-axis labels and line chart hard to read.

The desired rule for this codebase is:

- Use Element Plus layout components whenever the problem is page-level layout.
- Do not force all local presentation details into Element Plus components when plain CSS is a better fit.

For this change, the dashboard should follow that rule while prioritizing chart readability on small screens.

## Goals

- Move all page-level dashboard regions onto Element Plus grid structure.
- Keep the existing dashboard information architecture intact.
- Prevent the trend chart from becoming unreadable on small screens.
- Prefer readability over fully squeezing the chart into the viewport width.
- Limit the change to the dashboard page and its directly related styles.

## Non-Goals

- Redesigning dashboard visual style.
- Replacing charting technology.
- Converting every internal card sub-layout to Element Plus components.
- Refactoring unrelated responsive styles elsewhere in the admin app.

## Current State

The dashboard currently has three major regions:

1. A top metrics area built with `el-row.analysis-overview-grid` and responsive `el-col` items.
2. A middle trend card rendered as a standalone `section.chart-tabs-card`.
3. A bottom summary area built with `el-row.chart-grid` and responsive `el-col` items.

This means the page-level layout is inconsistent. The middle region does not participate in the same grid system as the surrounding regions.

On small screens, the chart container height adapts, but chart width still collapses to the viewport width. Because the chart has no minimum content width and no horizontal scrolling strategy, the rendered plot and labels become compressed.

## Proposed Approach

Use a dedicated Element Plus row for the trend region so every page-level section on the dashboard is expressed through `el-row` and `el-col`.

Within the trend card, add a two-layer chart container:

- An outer viewport container responsible for horizontal scrolling on narrow screens.
- An inner chart host container with a minimum width so the chart keeps a readable plotting area.

This keeps page-level layout in Element Plus while leaving chart rendering behavior to CSS and ECharts, which is the appropriate boundary for this page.

## Layout Design

### Page-Level Structure

The dashboard page will remain split into three regions:

1. Metrics grid
2. Trend grid row
3. Lower chart grid

The change is specifically that the trend region will become:

- `el-row` wrapper for page-level consistency
- Single `el-col :xs="24"` item spanning the full row width
- Existing trend card content nested inside that column

This preserves the current visual ordering while making the page structure consistent with the agreed layout rule.

### Trend Card Internal Structure

The trend card will keep its existing header, tabs, and chart content. Only the chart area structure will change:

1. Header remains in place.
2. Chart area gets a scroll viewport wrapper.
3. Actual chart mount node sits inside a min-width container.

This supports narrow screens without changing the card's meaning or interactions.

## Responsive Behavior

### Desktop and Tablet

- Trend card fills the full available width of its `el-col`.
- Horizontal scrolling remains inactive because the viewport is wide enough.
- Chart behaves close to its current desktop layout.

### Small Screens

- The card width continues to follow the screen width.
- The chart viewport allows horizontal scrolling.
- The chart host maintains a minimum width so the plot is not crushed.
- Users can horizontally pan the chart area to inspect labels and line segments.

This intentionally favors readable data over forcing the entire chart into a too-small width.

## Chart Behavior

The ECharts implementation should remain largely unchanged, but the chart config should adapt slightly for narrow screens.

Expected adjustments:

- Reduce x-axis label density on small screens.
- Optionally rotate x-axis labels when needed.
- Ensure chart resize logic reacts correctly after layout changes and when the viewport changes.

These changes are complementary to horizontal scrolling. Scrolling solves the hard width limit; label density tuning improves readability inside the visible window.

## Styling Strategy

Element Plus will own page-level layout only.

CSS will continue to own:

- Card internal spacing
- Trend header wrapping on narrow screens
- Horizontal scrolling behavior
- Minimum width for the chart host

This avoids overusing layout components in places where the content is better represented as normal document flow and chart container styling.

## Error Handling and Edge Cases

- If trend data is empty, the card layout should remain stable and not collapse awkwardly.
- If the screen is narrow and the chart width exceeds the viewport, only the chart area should scroll horizontally, not the entire page.
- If the chart is re-rendered after switching between 7-day and 30-day views, the chart should continue to size correctly inside the new wrapper structure.

## Testing Strategy

Testing should focus on behavior rather than cosmetic pixel matching.

Manual verification expectations:

1. Dashboard loads with the same information order as before.
2. Metrics row still stacks correctly at `xs`, `sm`, and `lg` breakpoints.
3. Trend card is now inside an Element Plus row/column structure.
4. On a narrow viewport, the trend chart no longer becomes unreadably compressed.
5. The chart area can scroll horizontally on small screens without causing page-level horizontal overflow.
6. The 7-day and 30-day toggle still re-renders the chart correctly.

If there are existing frontend tests around the dashboard, add or update only the minimum necessary coverage for the new structure or responsive container behavior.

## Implementation Boundaries

The implementation should be limited to:

- `src/pages/dashboard/DashboardPage.vue`
- Dashboard-related rules in `src/styles/main.css`
- Any minimal test files directly needed to cover the changed behavior

No unrelated responsive cleanup should be included in this change.

## Success Criteria

The change is successful when all of the following are true:

1. Every page-level region on the dashboard uses Element Plus row/column layout.
2. The trend card remains full-width in the dashboard flow.
3. On small screens, the trend chart remains readable because it keeps a protected minimum width.
4. Horizontal scrolling is contained to the chart area rather than the whole page.
5. Existing trend interactions and loading behavior continue to work.
