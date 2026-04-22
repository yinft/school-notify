function createAuthService({ request }) {
  return {
    async login({ code }) {
      const response = await request({
        url: '/auth/login',
        method: 'POST',
        data: { code }
      })

      return {
        userId: response.user_id,
        sessionToken: response.session_token,
        authProvider: response.auth_provider
      }
    },

    async logout() {
      await request({
        url: '/auth/logout',
        method: 'POST'
      })
    }
  }
}

module.exports = {
  createAuthService
}
