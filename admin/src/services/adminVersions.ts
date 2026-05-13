import { request } from './http'

export type AdminVersion = {
  id: number
  platform: string
  version: string
  build_number: string
  release_notes: string
  download_url: string
  file_size: number | null
  is_published: boolean
  is_recommended: boolean
  published_at: string | null
}

export type PaginatedVersionList = {
  items: AdminVersion[]
  total: number
  page: number
  page_size: number
}

export function fetchVersions(params?: { keyword?: string; page?: number; page_size?: number }) {
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
  return request<PaginatedVersionList>(`/api/admin/versions${suffix}`)
}

export function createVersion(payload: {
  platform: string
  version: string
  build_number: string
  release_notes: string
  download_url: string
  file_size: number | null
}) {
  return request<AdminVersion>('/api/admin/versions', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function updateVersion(id: number, payload: {
  release_notes?: string
  download_url?: string
  file_size?: number | null
}) {
  return request<AdminVersion>(`/api/admin/versions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}

export function publishVersion(id: number) {
  return request<AdminVersion>(`/api/admin/versions/${id}/publish`, {
    method: 'POST'
  })
}

export function unpublishVersion(id: number) {
  return request<AdminVersion>(`/api/admin/versions/${id}/unpublish`, {
    method: 'POST'
  })
}

export function recommendVersion(id: number) {
  return request<AdminVersion>(`/api/admin/versions/${id}/recommend`, {
    method: 'POST'
  })
}

export function deleteVersion(id: number) {
  return request<void>(`/api/admin/versions/${id}`, {
    method: 'DELETE'
  })
}
