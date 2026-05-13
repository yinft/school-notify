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
  const search = new URLSearchParams()
  if (params?.keyword) {
    search.set('keyword', params.keyword)
  }
  if (params?.sender_user_id) {
    search.set('sender_user_id', params.sender_user_id)
  }
  if (params?.page) {
    search.set('page', String(params.page))
  }
  if (params?.page_size) {
    search.set('page_size', String(params.page_size))
  }
  const suffix = search.size > 0 ? `?${search.toString()}` : ''
  return request<PaginatedNotificationList>(`/api/admin/notifications${suffix}`)
}

export function fetchNotificationDetail(notificationId: string) {
  return request<AdminNotificationDetail>(`/api/admin/notifications/${notificationId}`)
}
