const config = require('./config')
const { createAuthService } = require('./services/auth')
const { request } = require('./utils/request')
const { USER_PROFILE_STORAGE_KEY } = require('./utils/user-profile')
const {
  AUTH_SESSION_STORAGE_KEY,
  createPendingSession,
  createLoggedInSession,
  createLoggedOutSession,
  hasLoginSession,
  shouldAutoLogin
} = require('./utils/auth-session')

App({
  onLaunch() {
    const userProfile = wx.getStorageSync(USER_PROFILE_STORAGE_KEY)
    if (userProfile && userProfile.avatarUrl && userProfile.nickName) {
      this.globalData.userProfile = userProfile
    }

    const authSession = wx.getStorageSync(AUTH_SESSION_STORAGE_KEY)
    this.applyAuthSession(authSession || createPendingSession())

    if (shouldAutoLogin(authSession)) {
      this.ensureLogin().catch(() => {})
    }
  },

  applyAuthSession(session) {
    const nextSession = session && typeof session === 'object' ? session : createPendingSession()
    this.globalData.authSession = nextSession
    this.globalData.currentUserId = nextSession.currentUserId || ''
  },

  persistAuthSession(session) {
    this.applyAuthSession(session)
    wx.setStorageSync(AUTH_SESSION_STORAGE_KEY, session)
  },

  ensureLogin(options = {}) {
    const { manual = false } = options

    if (hasLoginSession(this.globalData.authSession)) {
      return Promise.resolve(this.globalData.authSession)
    }

    if (!manual && !shouldAutoLogin(this.globalData.authSession)) {
      return Promise.resolve(this.globalData.authSession)
    }

    if (this.loginPromise) {
      return this.loginPromise
    }

    this.loginPromise = new Promise((resolve, reject) => {
      wx.login({
        success: ({ code }) => {
          const authService = createAuthService({ request })
          authService
            .login({ code: code || '' })
            .then((loginResult) => {
              const session = createLoggedInSession({
                userId: loginResult.userId,
                loginCode: code || '',
                sessionToken: loginResult.sessionToken,
                authProvider: loginResult.authProvider
              })
              this.persistAuthSession(session)
              resolve(session)
            })
            .catch((error) => {
              this.persistAuthSession(createLoggedOutSession())
              if (manual) {
                wx.showToast({ title: '登录失败，请重试', icon: 'none' })
              }
              reject(error)
            })
        },
        fail: (error) => {
          this.persistAuthSession(createLoggedOutSession())
          if (manual) {
            wx.showToast({ title: '登录失败，请重试', icon: 'none' })
          }
          reject(error)
        },
        complete: () => {
          this.loginPromise = null
        }
      })
    })

    return this.loginPromise
  },

  setUserProfile(profile) {
    this.globalData.userProfile = profile
    wx.setStorageSync(USER_PROFILE_STORAGE_KEY, profile)
  },

  clearUserProfile() {
    this.globalData.userProfile = null
    wx.removeStorageSync(USER_PROFILE_STORAGE_KEY)
  },

  async logout() {
    const authSession = this.globalData.authSession
    if (authSession && authSession.sessionToken) {
      const authService = createAuthService({ request })
      try {
        await authService.logout()
      } catch {
        // Local logout should still succeed when backend session cleanup fails.
      }
    }

    this.persistAuthSession(createLoggedOutSession())
    this.clearUserProfile()
  },

  globalData: {
    apiBaseUrl: config.apiBaseUrl,
    currentUserId: '',
    userProfile: null,
    authSession: createPendingSession()
  }
})
