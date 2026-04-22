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

        reject({
          statusCode: response.statusCode,
          data: response.data,
          message: response.data && response.data.detail ? response.data.detail : 'request failed'
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
  buildRequestOptions
}
