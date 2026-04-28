const { envVersion } = wx.getAccountInfoSync().miniProgram

const CONFIGS = {
  develop: {
    apiBaseUrl: 'http://127.0.0.1:8000/api'
  },
  trial: {
    apiBaseUrl: 'https://www.schoolhelper.cn/api'
  },
  release: {
    apiBaseUrl: 'https://www.schoolhelper.cn/api'
  }
}

module.exports = CONFIGS[envVersion]
