const { createNotificationService } = require('../../services/notification')
const { request } = require('../../utils/request')

Page({
  data: {
    records: [],
    isLoading: false,
    errorText: ''
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
    this.loadRecords()
  },

  async loadRecords() {
    const app = getApp()
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isLoading: true, errorText: '' })

    try {
      const records = await notificationService.fetchNotificationRecords()
      this.setData({ records })
    } catch (error) {
      this.setData({ errorText: error.message || '记录加载失败' })
    } finally {
      this.setData({ isLoading: false })
    }
  },

  onPullDownRefresh() {
    this.loadRecords().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
