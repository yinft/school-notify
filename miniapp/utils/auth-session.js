const AUTH_SESSION_STORAGE_KEY = 'authSession'
const DEFAULT_USER_ID = 'user-001'

function createPendingSession() {
  return {
    isLoggedIn: false,
    currentUserId: '',
    loginCode: '',
    sessionToken: '',
    authProvider: '',
    requiresManualLogin: false
  }
}

function createLoggedInSession({ userId = DEFAULT_USER_ID, loginCode = '', sessionToken = '', authProvider = '' } = {}) {
  return {
    isLoggedIn: true,
    currentUserId: userId,
    loginCode,
    sessionToken,
    authProvider,
    requiresManualLogin: false
  }
}

function createLoggedOutSession() {
  return {
    isLoggedIn: false,
    currentUserId: '',
    loginCode: '',
    sessionToken: '',
    authProvider: '',
    requiresManualLogin: true
  }
}

function hasLoginSession(session) {
  return Boolean(session && session.isLoggedIn && session.currentUserId && session.sessionToken)
}

function shouldAutoLogin(session) {
  if (!session) {
    return true
  }

  return !session.requiresManualLogin && !hasLoginSession(session)
}

function getLoginRequiredMessage(pageTitle) {
  return `无法查看当前${pageTitle}页面，请登录`
}

module.exports = {
  AUTH_SESSION_STORAGE_KEY,
  DEFAULT_USER_ID,
  createPendingSession,
  createLoggedInSession,
  createLoggedOutSession,
  hasLoginSession,
  shouldAutoLogin,
  getLoginRequiredMessage
}
