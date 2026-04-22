const { ensurePageLogin } = require('../../utils/page-auth')
const { getLoginRequiredMessage } = require('../../utils/auth-session')
const { createLoginGateModel } = require('../../utils/login-gate')
const { syncProfileToServer } = require('../../utils/user-profile')

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

  authorizeProfile() {
    if (this.data.isLoginRequired || this.data.isSubmittingProfile) {
      return
    }

    if (!wx.getUserProfile) {
      wx.showToast({ title: '当前微信版本不支持', icon: 'none' })
      return
    }

    this.setData({ isSubmittingProfile: true })

    wx.getUserProfile({
      desc: '用于展示你的微信头像和昵称',
      success: async ({ userInfo }) => {
        const profile = {
          avatarUrl: userInfo.avatarUrl || '',
          nickName: userInfo.nickName || ''
        }

        const app = getApp()
        app.setUserProfile(profile)
        await syncProfileToServer({ nickname: profile.nickName, avatarUrl: profile.avatarUrl })
        this.syncProfile()
      },
      fail: () => {
        wx.showToast({ title: '未完成授权', icon: 'none' })
      },
      complete: () => {
        this.setData({ isSubmittingProfile: false })
      }
    })
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
