import { request } from './http'

export type AdminUserListItem = {
  user_id: string
  nickname: string | null
  avatar_url: string | null
  bound_devices_count: number
}

export type PaginatedUserList = {
  items: AdminUserListItem[]
  total: number
  page: number
  page_size: number
}

export type AdminUserDetail = {
  user_id: string
  nickname: string | null
  avatar_url: string | null
  devices: Array<{
    device_id: string
    device_name: string
    location_label: string
    client_version: string
    status: string
  }>
  recent_notifications: Array<{
    notification_id: string
    title: string
    created_at: string
  }>
}

export function fetchUsers(params?: { keyword?: string; page?: number; page_size?: number }) {
  return request<PaginatedUserList>('/api/admin/users', { params })
}

export function fetchUserDetail(userId: string) {
  return request<AdminUserDetail>(`/api/admin/users/${userId}`)
}
