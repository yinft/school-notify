const { createNotificationService } = require('../../services/notification')
const { ensurePageLogin } = require('../../utils/page-auth')
const { request } = require('../../utils/request')

const PAGE_SIZE = 10

Page({
  data: {
    records: [],
    isLoading: false,
    isLoadingMore: false,
    hasMore: false,
    totalRecords: 0,
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

  async loadRecords(options = {}) {
    const append = options.append === true
    if ((append && (this.data.isLoadingMore || !this.data.hasMore)) || (!append && this.data.isLoading)) {
      return
    }

    const app = getApp()
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData(append ? { isLoadingMore: true } : { isLoading: true, errorText: '', hasMore: false })

    try {
      const { records: rawRecords, total } = await notificationService.fetchNotificationRecords({
        limit: PAGE_SIZE,
        offset: append ? this.data.records.length : 0
      })
      const nextRecords = rawRecords.map((record) => ({
        ...record,
        levelText: this.getLevelText(record.level),
        createdAtText: this.formatCreatedAt(record.createdAt)
      }))
      const records = append ? this.data.records.concat(nextRecords) : nextRecords
      this.setData({
        records,
        totalRecords: total,
        hasMore: records.length < total,
        displayedCount: records.reduce(
          (total, record) => total + record.deliveries.filter((delivery) => delivery.displayed).length,
          0
        )
      })
    } catch (error) {
      if (append) {
        wx.showToast({ title: error.message || '加载更多失败', icon: 'none' })
      } else {
        this.setData({
          errorText: error.message || '记录加载失败',
          displayedCount: 0,
          totalRecords: 0,
          hasMore: false
        })
      }
    } finally {
      this.setData(append ? { isLoadingMore: false } : { isLoading: false })
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

    this.loadRecords({ append: false }).then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.isLoginRequired) {
      return
    }

    this.loadRecords({ append: true })
  }
})
