function request({ url, method = 'GET', data }) {
  const app = getApp()
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.apiBaseUrl}${url}`,
      method,
      data,
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
  request
}
