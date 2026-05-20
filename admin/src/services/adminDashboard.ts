import { request } from './http'

export type DashboardSummary = {
  device_count: number
  online_device_count: number
  user_count: number
  notification_count: number
  notification_trend: Array<{ date: string; count: number }>
  device_status_ratio: { online: number; offline: number }
  version_distribution: Array<{ client_version: string; device_count: number }>
}

export function fetchDashboardSummary() {
  return request<DashboardSummary>('/api/admin/dashboard/summary')
}

export function fetchDashboardNotificationTrend(params: { days: 7 | 30 }) {
  return request<{ items: DashboardSummary['notification_trend'] }>('/api/admin/dashboard/notification-trend', { params })
}
