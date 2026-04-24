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
    isAuthorizingLogin: false,
    isUnbinding: false
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
    const deviceService = createDeviceService({ request, currentUserId: app.globalData.currentUserId })

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

  async unbindDevice(event) {
    if (this.data.isUnbinding) {
      return
    }

    const { deviceId, deviceName } = event.currentTarget.dataset
    const confirmResult = await this.showUnbindConfirm(deviceName)

    if (!confirmResult.confirm) {
      return
    }

    const app = getApp()
    const deviceService = createDeviceService({ request, currentUserId: app.globalData.currentUserId })
    this.setData({ isUnbinding: true })

    try {
      await deviceService.unbindDevice({ deviceId })
      wx.showToast({ title: '设备已解绑', icon: 'none' })
      await this.loadDevices()
    } catch (error) {
      wx.showToast({ title: error.message || '解绑失败', icon: 'none' })
    } finally {
      this.setData({ isUnbinding: false })
    }
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
  showUnbindConfirm(deviceName) {
    return new Promise((resolve) => {
      wx.showModal({
        title: '确认解绑设备',
        content: `解绑后，你将无法继续向“${deviceName}”发送通知。是否继续？`,
        confirmColor: '#d64545',
        success: resolve,
        fail: () => resolve({ confirm: false })
      })
    })
  },
