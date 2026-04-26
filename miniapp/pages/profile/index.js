const { ensurePageLogin } = require('../../utils/page-auth')
const { getLoginRequiredMessage } = require('../../utils/auth-session')
const { createLoginGateModel } = require('../../utils/login-gate')
const { createUserProfile, syncProfileToServer } = require('../../utils/user-profile')

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
    const profile = createUserProfile({ avatarUrl, nickName: this.data.nickName || '微信用户' })
    const app = getApp()
    app.setUserProfile(profile)
    await syncProfileToServer({ nickname: profile.nickName, avatarUrl })
    this.setData({ isSubmittingProfile: false })
    wx.showToast({ title: '头像已更新', icon: 'none' })
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
  }
})
