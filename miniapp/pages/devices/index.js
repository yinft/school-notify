const { createDeviceService } = require('../../services/device')
const { request } = require('../../utils/request')

function checkAuth() {
  const app = getApp()
  const p = app.globalData.userProfile
  if (!p || !p.avatarUrl || !p.nickName) {
    wx.redirectTo({ url: '/pages/auth/index' })
    return false
  }
  return true
}

Page({
  data: {
    devices: [],
    isLoading: false,
    errorText: '',
    onlineCount: 0
  },

  onShow() {
    if (!checkAuth()) return
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
      this.setData({
        devices,
        onlineCount: devices.filter((device) => device.status === 'online').length
      })
    } catch (error) {
      this.setData({
        errorText: error.message || '设备加载失败',
        onlineCount: 0
      })
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
