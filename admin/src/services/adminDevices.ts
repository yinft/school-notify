import { request } from './http'

export type AdminDeviceListItem = {
  device_id: string
  device_name: string
  location_label: string
  client_version: string
  status: string
  bound_users_count: number
}

export type PaginatedDeviceList = {
  items: AdminDeviceListItem[]
  total: number
  page: number
  page_size: number
}

export type AdminDeviceDetail = {
  device_id: string
  device_name: string
  location_label: string
  client_version: string
  status: string
  bound_users: Array<{ user_id: string; nickname: string | null }>
  recent_notifications: Array<{ notification_id: string; title: string; sender_user_id: string }>
}

export function fetchDevices(params?: { keyword?: string; status?: string; page?: number; page_size?: number }) {
  const search = new URLSearchParams()
  if (params?.keyword) {
    search.set('keyword', params.keyword)
  }
  if (params?.status) {
    search.set('status', params.status)
  }
  if (params?.page) {
    search.set('page', String(params.page))
  }
  if (params?.page_size) {
    search.set('page_size', String(params.page_size))
  }
  const suffix = search.size > 0 ? `?${search.toString()}` : ''
  return request<PaginatedDeviceList>(`/api/admin/devices${suffix}`)
}

export function fetchDeviceDetail(deviceId: string) {
  return request<AdminDeviceDetail>(`/api/admin/devices/${deviceId}`)
}

export function updateDevice(deviceId: string, payload: { device_name?: string; location_label?: string }) {
  return request<AdminDeviceListItem>(`/api/admin/devices/${deviceId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}

export function unbindDeviceUser(deviceId: string, userId: string) {
  return request<void>(`/api/admin/devices/${deviceId}/bindings/${userId}`, {
    method: 'DELETE'
  })
}
