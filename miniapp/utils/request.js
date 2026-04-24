const { AUTH_SESSION_STORAGE_KEY, createLoggedOutSession } = require('./auth-session')

function buildRequestOptions({ apiBaseUrl, authSession, url, method = 'GET', data }) {
  const header = {}
  if (authSession && authSession.sessionToken) {
    header.Authorization = `Bearer ${authSession.sessionToken}`
  }

  return {
    url: `${apiBaseUrl}${url}`,
    method,
    data,
    header
  }
}

function getErrorMessage(data) {
  if (!data || !data.detail) {
    return 'request failed'
  }
  if (typeof data.detail === 'string') {
    return data.detail
  }
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg || String(item)).join('；')
  }
  return String(data.detail)
}

function clearSessionOnUnauthorized(statusCode) {
  if (statusCode !== 401) {
    return
  }
  const loggedOutSession = createLoggedOutSession()
  const app = getApp()
  if (app && app.globalData) {
    app.globalData.authSession = loggedOutSession
  }
  wx.setStorageSync(AUTH_SESSION_STORAGE_KEY, loggedOutSession)
}

function request({ url, method = 'GET', data }) {
  const app = getApp()
  const requestOptions = buildRequestOptions({
    apiBaseUrl: app.globalData.apiBaseUrl,
    authSession: app.globalData.authSession,
    url,
    method,
    data
  })

  return new Promise((resolve, reject) => {
    wx.request({
      ...requestOptions,
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data)
          return
        }

        clearSessionOnUnauthorized(response.statusCode)
        reject({
          statusCode: response.statusCode,
          data: response.data,
          message: getErrorMessage(response.data)
        })
      },
      fail(error) {
        reject({
          message: error.errMsg || 'network error'
        })
      }
    })
  })
}

module.exports = {
  request,
  buildRequestOptions,
  getErrorMessage
}
