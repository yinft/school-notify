const config = require('./config')
const { USER_PROFILE_STORAGE_KEY } = require('./utils/user-profile')

App({
  onLaunch() {
    const userProfile = wx.getStorageSync(USER_PROFILE_STORAGE_KEY)
    if (userProfile && userProfile.avatarUrl && userProfile.nickName) {
      this.globalData.userProfile = userProfile
    }
  },

  globalData: {
    apiBaseUrl: config.apiBaseUrl,
    currentUserId: 'user-001',
    userProfile: null
  }
})
