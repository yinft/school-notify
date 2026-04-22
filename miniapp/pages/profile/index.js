const { USER_PROFILE_STORAGE_KEY } = require('../../utils/user-profile')

Page({
  data: {
    userId: '',
    avatarUrl: '',
    nickName: ''
  },

  onShow() {
    const app = getApp()
    const profile = app.globalData.userProfile || {}
    this.setData({
      userId: app.globalData.currentUserId,
      avatarUrl: profile.avatarUrl || '',
      nickName: profile.nickName || ''
    })
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
    }
  },

  goToBind() {
    wx.navigateTo({ url: '/pages/bind/index' })
  },

  goToRecords() {
    wx.switchTab({ url: '/pages/records/index' })
  }
})
