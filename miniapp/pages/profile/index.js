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
      nickName: profile.nickName || ''
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

  onChooseAvatar(event) {
    if (this.data.isLoginRequired || this.data.isSubmittingProfile) {
      return
    }

    this.setData({ avatarUrl: event.detail.avatarUrl || '' })
  },

  onNicknameInput(event) {
    this.setData({ nickName: event.detail.value || '' })
  },

  async saveProfile() {
    if (this.data.isLoginRequired || this.data.isSubmittingProfile) {
      return
    }

    const profile = createUserProfile({
      avatarUrl: this.data.avatarUrl,
      nickName: this.data.nickName
    })

    if (!profile.avatarUrl || !profile.nickName) {
      wx.showToast({ title: '请选择头像并填写昵称', icon: 'none' })
      return
    }

    this.setData({ isSubmittingProfile: true })

    const app = getApp()
    app.setUserProfile(profile)
    const result = await syncProfileToServer({ nickname: profile.nickName, avatarUrl: profile.avatarUrl })
    this.setData({ isSubmittingProfile: false })
    this.syncProfile()
    wx.showToast({ title: result ? '资料已保存' : '已本地保存', icon: 'none' })
  },

  async logout() {
    const app = getApp()
    await app.logout()
    this.setData({
      userId: '',
      avatarUrl: '',
      nickName: '',
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
