const { createNotificationService } = require('../../services/notification')
const { ensurePageLogin } = require('../../utils/page-auth')
const { request } = require('../../utils/request')

Page({
  data: {
    records: [],
    isLoading: false,
    errorText: '',
    displayedCount: 0,
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false
  },

  async onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
    if (!(await ensurePageLogin(this, '发送记录'))) {
      return
    }
    this.loadRecords()
  },

  async manualLogin() {
    if (this.data.isAuthorizingLogin) {
      return
    }

    this.setData({ isAuthorizingLogin: true })
    if (await ensurePageLogin(this, '发送记录', { manual: true })) {
      this.loadRecords()
    }
  },

  async loadRecords() {
    const app = getApp()
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isLoading: true, errorText: '' })

    try {
      const { records: rawRecords } = await notificationService.fetchNotificationRecords()
      const records = rawRecords.map((record) => ({
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
    if (this.data.isLoginRequired) {
      wx.stopPullDownRefresh()
      return
    }

    this.loadRecords().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
