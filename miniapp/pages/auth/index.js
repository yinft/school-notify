const { USER_PROFILE_STORAGE_KEY } = require('../../utils/user-profile')

Page({
  data: {
    isSubmitting: false
  },

  onShow() {
    const app = getApp()
    const p = app.globalData.userProfile
    if (p && p.avatarUrl && p.nickName) {
      wx.switchTab({ url: '/pages/devices/index' })
    }
  },

  authorizeProfile() {
    if (!wx.getUserProfile) {
      wx.showToast({ title: '当前微信版本不支持', icon: 'none' })
      return
    }

    this.setData({ isSubmitting: true })

    wx.getUserProfile({
      desc: '用于展示你的微信头像和昵称',
      success: ({ userInfo }) => {
        const profile = {
          avatarUrl: userInfo.avatarUrl || '',
          nickName: userInfo.nickName || ''
        }

        const app = getApp()
        app.globalData.userProfile = profile
        wx.setStorageSync(USER_PROFILE_STORAGE_KEY, profile)
        wx.switchTab({ url: '/pages/devices/index' })
      },
      fail: () => {
        wx.showToast({ title: '未完成授权', icon: 'none' })
      },
      complete: () => {
        this.setData({ isSubmitting: false })
      }
    })
  }
})
