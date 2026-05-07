const { envVersion } = wx.getAccountInfoSync().miniProgram
const CONFIGS = {
  develop: {
    apiBaseUrl: 'http://127.0.0.1:8000/api'
  },
  trial: {
    apiBaseUrl: 'http://8.136.61.23:8000/api'
  },
  release: {
    apiBaseUrl: 'https://www.schoolhelper.cn/api'
  }
}

module.exports = CONFIGS[envVersion]
