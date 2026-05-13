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
    { label: '设备总数', value: value.device_count, tone: 'ink' },
    { label: '在线设备', value: value.online_device_count, tone: 'mint' },
    { label: '用户总数', value: value.user_count, tone: 'gold' },
    { label: '通知记录', value: value.notification_count, tone: 'violet' }
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
        axisLine: { lineStyle: { color: '#b7c3d6' } },
        axisLabel: { color: '#66758c' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(18, 32, 51, 0.08)' } },
        axisLabel: { color: '#66758c' }
      },
      series: [{
        type: 'line',
        smooth: true,
        data: summary.value.notification_trend.map((item) => item.count),
        lineStyle: { color: '#1d5cff', width: 3 },
        itemStyle: { color: '#1d5cff' },
        areaStyle: { color: 'rgba(29, 92, 255, 0.12)' }
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
        label: { color: '#122033' },
        data: [
          { value: summary.value.device_status_ratio.online, name: '在线', itemStyle: { color: '#19b17f' } },
          { value: summary.value.device_status_ratio.offline, name: '离线', itemStyle: { color: '#9ca9bc' } }
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
        axisLine: { lineStyle: { color: '#b7c3d6' } },
        axisLabel: { color: '#66758c' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(18, 32, 51, 0.08)' } },
        axisLabel: { color: '#66758c' }
      },
      series: [{
        type: 'bar',
        barWidth: 30,
        data: summary.value.version_distribution.map((item) => ({ value: item.device_count, itemStyle: { color: '#7a56ff' } }))
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
  <div class="page-stack">
    <section class="hero-panel compact">
      <div>
        <p class="section-eyebrow">Overview</p>
        <h2>后台总览</h2>
        <span>先给出运营概览卡片，图表位保留在下方做渐进增强。</span>
      </div>
    </section>

    <section v-if="errorMessage" class="feedback-banner error-banner standalone-banner">
      <span>{{ errorMessage }}</span>
      <el-button text type="primary" @click="$router.go(0)">重试</el-button>
    </section>

    <section class="card-grid four-up">
      <article v-for="card in cards" :key="card.label" class="metric-card" :data-tone="card.tone" v-loading="loading">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
      </article>
    </section>

    <section class="chart-grid">
      <article class="chart-card" v-loading="loading">
        <h3>最近 7 天通知趋势</h3>
        <div ref="trendChart" class="echart-canvas"></div>
      </article>
      <article class="chart-card" v-loading="loading">
        <h3>在线设备占比</h3>
        <div ref="statusChart" class="echart-canvas"></div>
      </article>
      <article class="chart-card" v-loading="loading">
        <h3>客户端版本分布</h3>
        <div ref="versionChart" class="echart-canvas"></div>
      </article>
    </section>
  </div>
</template>
