import axios, { AxiosError, type AxiosProgressEvent, type AxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY = 'school-notify-admin-token'

type RequestOptions = {
  method?: AxiosRequestConfig['method']
  params?: Record<string, unknown>
  data?: unknown
  headers?: Record<string, string>
  auth?: boolean
  responseType?: AxiosRequestConfig['responseType']
  onUploadProgress?: (event: AxiosProgressEvent) => void
}

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
})

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

function getErrorDetail(data: unknown) {
  if (typeof data !== 'object' || data === null || !('detail' in data)) {
    return ''
  }

  const detail = data.detail
  return typeof detail === 'string' ? detail : ''
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  try {
    const token = options.auth === false ? '' : getToken()
    const response = await http.request<T>({
      url: path,
      method: options.method,
      params: options.params,
      data: options.data,
      headers: {
        ...(options.data instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      responseType: options.responseType,
      onUploadProgress: options.onUploadProgress,
      validateStatus: () => true
    })

    if (response.status === 401 && options.auth !== false) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      throw new Error('登录已过期，请重新登录')
    }

    if (response.status === 204) {
      return undefined as T
    }

    if (response.status < 200 || response.status >= 300) {
      throw new Error(getErrorDetail(response.data) || 'request failed')
    }

    return response.data
  } catch (error) {
    if (error instanceof Error && !(error instanceof AxiosError)) {
      throw error
    }

    const axiosError = error as AxiosError<{ detail?: string }>
    throw new Error(axiosError.response?.data?.detail || axiosError.message || 'request failed')
  }
}
