import { request } from './http'

export type AdminNotificationListItem = {
  notification_id: string
  sender_user_id: string
  title: string
  created_at: string
  success_count: number
  failed_count: number
}

export type PaginatedNotificationList = {
  items: AdminNotificationListItem[]
  total: number
  page: number
  page_size: number
}

export type AdminNotificationDetail = {
  notification_id: string
  sender_user_id: string
  title: string
  content: string
  created_at: string
  deliveries: Array<{
    device_id: string
    device_name: string
    received: boolean
    displayed: boolean
    spoken: boolean
    failed: boolean
    error_message: string | null
  }>
}

export function fetchNotifications(params?: { keyword?: string; sender_user_id?: string; page?: number; page_size?: number }) {
  return request<PaginatedNotificationList>('/api/admin/notifications', { params })
}

export function fetchNotificationDetail(notificationId: string) {
  return request<AdminNotificationDetail>(`/api/admin/notifications/${notificationId}`)
}
