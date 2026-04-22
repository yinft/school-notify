const { hasLoginSession, getLoginRequiredMessage } = require('./auth-session')
const { createLoginGateModel } = require('./login-gate')

async function ensurePageLogin(page, pageTitle, options = {}) {
  const app = getApp()

  try {
    const session = await app.ensureLogin(options)
    if (hasLoginSession(session)) {
      page.setData({
        isLoginRequired: false,
        loginTipText: '',
        loginGate: null,
        isAuthorizingLogin: false
      })
      return true
    }
  } catch {
    // Manual login failure falls back to the inline login prompt.
  }

  page.setData({
    isLoginRequired: true,
    loginTipText: getLoginRequiredMessage(pageTitle),
    loginGate: createLoginGateModel(pageTitle),
    isAuthorizingLogin: false
  })
  return false
}

module.exports = {
  ensurePageLogin
}
