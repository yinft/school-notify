const app = getApp()

Page({
  data: {
    userId: ''
  },

  onShow() {
    this.setData({ userId: app.globalData.currentUserId })
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
