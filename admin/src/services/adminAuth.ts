import { request } from './http'

export type AdminSession = {
  username: string
  display_name: string
  session_token: string
}

export type AdminProfile = {
  username: string
  display_name: string
}

export function loginAdmin(payload: { username: string; password: string }) {
  return request<AdminSession>('/api/admin/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
    auth: false
  })
}

export function getAdminProfile() {
  return request<AdminProfile>('/api/admin/auth/me')
}

export function logoutAdmin() {
  return request<void>('/api/admin/auth/logout', {
    method: 'POST'
  })
}
