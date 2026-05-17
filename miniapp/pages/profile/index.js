const { ensurePageLogin } = require('../../utils/page-auth')
const { getLoginRequiredMessage } = require('../../utils/auth-session')
const { createLoginGateModel } = require('../../utils/login-gate')
const { createUserProfile, uploadAvatarToQiniu } = require('../../utils/user-profile')

Page({
  data: {
    userId: '',
    avatarUrl: '',
    nickName: '',
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false,
    isSubmittingProfile: false
  },

  async onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
    }
    if (!(await ensurePageLogin(this, '我的'))) {
      return
    }
    this.syncProfile()
  },

  syncProfile() {
    const app = getApp()
    const profile = app.globalData.userProfile || {}
    this.setData({
      userId: app.globalData.currentUserId,
      avatarUrl: profile.avatarUrl || '',
      nickName: profile.nickName || '微信用户'
    })
  },

  async manualLogin() {
    if (this.data.isAuthorizingLogin) {
      return
    }

    this.setData({ isAuthorizingLogin: true })
    if (await ensurePageLogin(this, '我的', { manual: true })) {
      this.syncProfile()
    }
  },

  async onChooseAvatar(event) {
    if (this.data.isLoginRequired || this.data.isSubmittingProfile) {
      return
    }

    const avatarUrl = event.detail.avatarUrl || ''
    this.setData({ avatarUrl })

    if (!avatarUrl) return

    this.setData({ isSubmittingProfile: true })
    try {
      const nickName = this.data.nickName || '微信用户'
      const permanentAvatarUrl = await uploadAvatarToQiniu({ filePath: avatarUrl, nickname: nickName })
      const profile = createUserProfile({ avatarUrl: permanentAvatarUrl, nickName })
      const app = getApp()
      app.setUserProfile(profile)
      this.setData({ avatarUrl: permanentAvatarUrl })
      wx.showToast({ title: '头像已更新', icon: 'none' })
    } catch {
      this.syncProfile()
      wx.showToast({ title: '头像上传失败', icon: 'none' })
    } finally {
      this.setData({ isSubmittingProfile: false })
    }
  },

  async logout() {
    const app = getApp()
    await app.logout()
    this.setData({
      userId: '',
      avatarUrl: '',
      isLoginRequired: true,
      loginTipText: getLoginRequiredMessage('我的'),
      loginGate: createLoginGateModel('我的')
    })
  },

  goToBind() {
    wx.navigateTo({ url: '/pages/bind/index' })
  },

  goToRecords() {
    wx.switchTab({ url: '/pages/records/index' })
  },

  copyWechat() {
    wx.setClipboardData({ data: 'Y840013505' })
  },

  copyEmail() {
    wx.setClipboardData({ data: '840013505@qq.com' })
  }
})
