const { createDeviceService } = require('../../services/device')
const { ensurePageLogin } = require('../../utils/page-auth')
const { request } = require('../../utils/request')

Page({
  data: {
    devices: [],
    isLoading: false,
    errorText: '',
    onlineCount: 0,
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false
  },

  async onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
    if (!(await ensurePageLogin(this, '设备列表'))) {
      return
    }
    this.loadDevices()
  },

  async manualLogin() {
    if (this.data.isAuthorizingLogin) {
      return
    }

    this.setData({ isAuthorizingLogin: true })
    if (await ensurePageLogin(this, '设备列表', { manual: true })) {
      this.loadDevices()
    }
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
    if (this.data.isLoginRequired) {
      wx.stopPullDownRefresh()
      return
    }

    this.loadDevices().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
