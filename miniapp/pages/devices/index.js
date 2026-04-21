const { createDeviceService } = require('../../services/device')
const { request } = require('../../utils/request')

Page({
  data: {
    devices: [],
    isLoading: false,
    errorText: ''
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
    this.loadDevices()
  },

  async loadDevices() {
    const app = getApp()
    const deviceService = createDeviceService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isLoading: true, errorText: '' })

    try {
      const devices = await deviceService.fetchUserDevices()
      this.setData({ devices })
    } catch (error) {
      this.setData({ errorText: error.message || '设备加载失败' })
    } finally {
      this.setData({ isLoading: false })
    }
  },

  goToBind() {
    wx.navigateTo({ url: '/pages/bind/index' })
  },

  onPullDownRefresh() {
    this.loadDevices().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
