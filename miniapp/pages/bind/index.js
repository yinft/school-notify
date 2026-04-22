const { createBindingService, extractBindCodeFromScan, normalizeBindCode } = require('../../services/binding')
const { ensurePageLogin } = require('../../utils/page-auth')
const { request } = require('../../utils/request')

Page({
  data: {
    code: '',
    isSubmitting: false,
    helperText: '请输入 Windows 客户端展示的 6 位绑定码',
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false
  },

  async onShow() {
    await ensurePageLogin(this, '设备绑定')
  },

  async manualLogin() {
    if (this.data.isAuthorizingLogin) {
      return
    }

    this.setData({ isAuthorizingLogin: true })
    await ensurePageLogin(this, '设备绑定', { manual: true })
  },

  onCodeInput(event) {
    this.setData({
      code: normalizeBindCode(event.detail.value)
    })
  },

  scanCode() {
    wx.scanCode({
      onlyFromCamera: false,
      success: (result) => {
        const code = extractBindCodeFromScan(result.result)
        if (!code) {
          wx.showToast({ title: '未识别到绑定码', icon: 'none' })
          return
        }

        this.setData({ code })
      },
      fail: () => {
        wx.showToast({ title: '扫码已取消', icon: 'none' })
      }
    })
  },

  async submit() {
    const { code, isSubmitting } = this.data
    if (isSubmitting) {
      return
    }

    if (this.data.isLoginRequired) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    if (!code) {
      wx.showToast({ title: '请输入绑定码', icon: 'none' })
      return
    }

    const app = getApp()
    const bindingService = createBindingService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isSubmitting: true })

    try {
      const result = await bindingService.bindDevice({ code })
      wx.showToast({ title: '绑定成功', icon: 'success' })
      this.setData({
        code: '',
        helperText: `已绑定设备：${result.device_id}`
      })
      setTimeout(() => {
        wx.navigateBack({ delta: 1 })
      }, 500)
    } catch (error) {
      wx.showToast({
        title: error.message || '绑定失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isSubmitting: false })
    }
  }
})
