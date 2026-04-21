const config = require('./config')

App({
  globalData: {
    apiBaseUrl: config.apiBaseUrl,
    currentUserId: 'user-001'
  }
})
