const { ensurePageLogin } = require('../../utils/page-auth')
const { getLoginRequiredMessage } = require('../../utils/auth-session')
const { createLoginGateModel } = require('../../utils/login-gate')
const { createUserProfile, hasAuthorizedProfile, syncProfileToServer, uploadAvatarToQiniu } = require('../../utils/user-profile')

Page({
  data: {
    userId: '',
    avatarUrl: '',
    nickName: '',
    draftNickName: '',
    showProfileSyncPrompt: false,
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false,
    isSubmittingProfile: false,
    isProfileReady: false
  },

  async onShow() {
    wx.setNavigationBarTitle({ title: '我的' })
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
    }
    if (!(await ensurePageLogin(this, '我的'))) {
      this.setData({ isProfileReady: true })
      return
    }
    this.syncProfile()
  },

  syncProfile() {
    const app = getApp()
    const profile = createUserProfile(app.globalData.userProfile || {})
    this.setData({
      userId: app.globalData.currentUserId,
      avatarUrl: profile.avatarUrl || '',
      nickName: profile.nickName || '微信用户',
      draftNickName: profile.nickName || '',
      nickNamePlaceholder: profile.nickName || '请输入昵称',
      showProfileSyncPrompt: !hasAuthorizedProfile(profile),
      isProfileReady: true
    })
  },

  async onNickNameConfirm(event) {
    if (this.data.isLoginRequired || this.data.isSubmittingProfile) {
      return
    }

    const nickName = event.detail && typeof event.detail.value === 'string' ? event.detail.value : ''
    const profile = createUserProfile({ avatarUrl: this.data.avatarUrl || '', nickName })
    if (!profile.nickName) {
      return
    }

    const currentNickName = createUserProfile({ nickName: this.data.nickName === '微信用户' ? '' : this.data.nickName }).nickName
    if (profile.nickName === currentNickName) {
      return
    }

    this.setData({ isSubmittingProfile: true })
    try {
      await syncProfileToServer({ nickname: profile.nickName })
      const app = getApp()
      app.setUserProfile(createUserProfile({ avatarUrl: this.data.avatarUrl, nickName: profile.nickName }))
      this.syncProfile()
      wx.showToast({ title: '微信昵称已更新', icon: 'none' })
    } catch {
      this.syncProfile()
      wx.showToast({ title: '昵称更新失败', icon: 'none' })
    } finally {
      this.setData({ isSubmittingProfile: false })
    }
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
      const nickName = createUserProfile({ nickName: this.data.nickName === '微信用户' ? '' : this.data.nickName }).nickName
      const permanentAvatarUrl = await uploadAvatarToQiniu({ filePath: avatarUrl, nickname: nickName })
      const app = getApp()
      app.setUserProfile(createUserProfile({ avatarUrl: permanentAvatarUrl, nickName: this.data.draftNickName || nickName }))
      this.syncProfile()
      wx.showToast({ title: '微信头像已更新', icon: 'none' })
    } catch {
      this.syncProfile()
      wx.showToast({ title: '头像更新失败', icon: 'none' })
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
      nickName: '',
    draftNickName: '',
    nickNamePlaceholder: '',
      showProfileSyncPrompt: false,
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
