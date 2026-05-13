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
  const search = new URLSearchParams()
  if (params?.keyword) {
    search.set('keyword', params.keyword)
  }
  if (params?.page) {
    search.set('page', String(params.page))
  }
  if (params?.page_size) {
    search.set('page_size', String(params.page_size))
  }
  const suffix = search.size > 0 ? `?${search.toString()}` : ''
  return request<PaginatedUserList>(`/api/admin/users${suffix}`)
}

export function fetchUserDetail(userId: string) {
  return request<AdminUserDetail>(`/api/admin/users/${userId}`)
}
