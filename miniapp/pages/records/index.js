const { createNotificationService } = require('../../services/notification')
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
    records: [],
    isLoading: false,
    errorText: '',
    displayedCount: 0
  },

  onShow() {
    if (!checkAuth()) return
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
    this.loadRecords()
  },

  async loadRecords() {
    const app = getApp()
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isLoading: true, errorText: '' })

    try {
      const records = (await notificationService.fetchNotificationRecords()).map((record) => ({
        ...record,
        levelText: this.getLevelText(record.level),
        createdAtText: this.formatCreatedAt(record.createdAt)
      }))
      this.setData({
        records,
        displayedCount: records.reduce(
          (total, record) => total + record.deliveries.filter((delivery) => delivery.displayed).length,
          0
        )
      })
    } catch (error) {
      this.setData({
        errorText: error.message || '记录加载失败',
        displayedCount: 0
      })
    } finally {
      this.setData({ isLoading: false })
    }
  },

  getLevelText(level) {
    return {
      normal: '普通',
      important: '重要',
      urgent: '紧急'
    }[level] || level
  },

  formatCreatedAt(createdAt) {
    if (!createdAt) {
      return ''
    }

    const date = new Date(createdAt)
    if (Number.isNaN(date.getTime())) {
      return ''
    }

    const pad = (value) => String(value).padStart(2, '0')

    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
  },

  onPullDownRefresh() {
    this.loadRecords().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
