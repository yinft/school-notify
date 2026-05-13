import { defineStore } from 'pinia'

import { getAdminProfile, loginAdmin, logoutAdmin, type AdminProfile, type AdminSession } from '../services/adminAuth'

type AuthState = {
  sessionToken: string
  profile: AdminProfile | null
  hydrating: boolean
}

const TOKEN_KEY = 'school-notify-admin-token'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    sessionToken: localStorage.getItem(TOKEN_KEY) || '',
    profile: null,
    hydrating: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.sessionToken)
  },
  actions: {
    async login(username: string, password: string) {
      const session: AdminSession = await loginAdmin({ username, password })
      this.sessionToken = session.session_token
      this.profile = {
        username: session.username,
        display_name: session.display_name
      }
      localStorage.setItem(TOKEN_KEY, session.session_token)
    },
    async hydrate() {
      if (!this.sessionToken) {
        return
      }
      this.hydrating = true
      try {
        this.profile = await getAdminProfile()
      } catch {
        this.clear()
      } finally {
        this.hydrating = false
      }
    },
    async logout() {
      if (this.sessionToken) {
        try {
          await logoutAdmin()
        } finally {
          this.clear()
        }
      }
    },
    clear() {
      this.sessionToken = ''
      this.profile = null
      this.hydrating = false
      localStorage.removeItem(TOKEN_KEY)
    }
  }
})
