<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useTemplateRef, watch } from 'vue'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

import { fetchDashboardSummary, type DashboardSummary } from '../../services/adminDashboard'

const summary = ref<DashboardSummary | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const trendChartRef = useTemplateRef<HTMLDivElement>('trendChart')
const statusChartRef = useTemplateRef<HTMLDivElement>('statusChart')
const versionChartRef = useTemplateRef<HTMLDivElement>('versionChart')
let echartsCore: typeof import('echarts/core') | null = null

const cards = computed(() => {
  const value = summary.value
  if (!value) {
    return []
  }

  return [
    { label: '设备总数', value: value.device_count, totalTitle: '在线设备', totalValue: value.online_device_count, tone: 'blue' },
    { label: '在线设备', value: value.online_device_count, totalTitle: '离线设备', totalValue: value.device_status_ratio.offline, tone: 'green' },
    { label: '用户总数', value: value.user_count, totalTitle: '通知记录', totalValue: value.notification_count, tone: 'amber' },
    {
      label: '通知记录',
      value: value.notification_count,
      totalTitle: '最近趋势',
      totalValue: value.notification_trend.reduce((sum, item) => sum + item.count, 0),
      tone: 'violet'
    }
  ]
})

async function renderCharts() {
  if (!summary.value) {
    return
  }

  if (!echartsCore) {
    const module = await import('echarts/core')
    module.use([CanvasRenderer, LineChart, PieChart, BarChart, GridComponent, TooltipComponent, LegendComponent])
    echartsCore = module
  }

  const echarts = echartsCore

  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      grid: { left: 24, right: 8, top: 20, bottom: 24 },
      xAxis: {
        type: 'category',
        data: summary.value.notification_trend.map((item) => item.date.slice(5)),
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { color: '#71717a' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(5, 5, 5, 0.06)' } },
        axisLabel: { color: '#71717a' }
      },
      series: [{
        type: 'line',
        smooth: true,
        data: summary.value.notification_trend.map((item) => item.count),
        lineStyle: { color: '#1677ff', width: 3 },
        itemStyle: { color: '#1677ff' },
        areaStyle: { color: 'rgba(22, 119, 255, 0.12)' }
      }]
    })
  }

  if (statusChartRef.value) {
    const chart = echarts.init(statusChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['55%', '78%'],
        label: { color: '#303033' },
        data: [
          { value: summary.value.device_status_ratio.online, name: '在线', itemStyle: { color: '#52c41a' } },
          { value: summary.value.device_status_ratio.offline, name: '离线', itemStyle: { color: '#d9d9d9' } }
        ]
      }]
    })
  }

  if (versionChartRef.value) {
    const chart = echarts.init(versionChartRef.value)
    chart.setOption({
      grid: { left: 24, right: 8, top: 20, bottom: 24 },
      xAxis: {
        type: 'category',
        data: summary.value.version_distribution.map((item) => item.client_version),
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { color: '#71717a' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(5, 5, 5, 0.06)' } },
        axisLabel: { color: '#71717a' }
      },
      series: [{
        type: 'bar',
        barWidth: 30,
        data: summary.value.version_distribution.map((item) => ({ value: item.device_count, itemStyle: { color: '#1677ff' } }))
      }]
    })
  }
}

onMounted(async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    summary.value = await fetchDashboardSummary()
    await nextTick()
    await renderCharts()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '仪表盘加载失败'
  } finally {
    loading.value = false
  }
})

watch(summary, async () => {
  await nextTick()
  await renderCharts()
})
</script>

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
