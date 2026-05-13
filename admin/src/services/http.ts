const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

type RequestOptions = RequestInit & {
  auth?: boolean
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers || {})
  headers.set('Content-Type', 'application/json')

  if (options.auth !== false) {
    const token = localStorage.getItem('school-notify-admin-token') || ''
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: 'request failed' }))
    if (response.status === 401 && options.auth !== false) {
      localStorage.removeItem('school-notify-admin-token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      throw new Error('登录已过期，请重新登录')
    }
    throw new Error(payload.detail || 'request failed')
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}
