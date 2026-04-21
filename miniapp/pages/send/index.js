const { createDeviceService } = require('../../services/device')
const { createNotificationService } = require('../../services/notification')
const { request } = require('../../utils/request')

Page({
  data: {
    levels: ['normal', 'important', 'urgent'],
    durations: ['10 秒', '30 秒', '60 秒', '常驻'],
    levelIndex: 0,
    durationIndex: 1,
    title: '',
    content: '',
    devices: [],
    selectedDeviceIds: [],
    isSubmitting: false,
    isLoadingDevices: false,
    errorText: ''
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    this.loadDevices()
  },

  async loadDevices() {
    const app = getApp()
    const deviceService = createDeviceService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isLoadingDevices: true, errorText: '' })

    try {
      const devices = await deviceService.fetchUserDevices()
      const onlineDevices = devices.filter((device) => device.status === 'online')
      this.setData({
        devices: onlineDevices,
        selectedDeviceIds: onlineDevices.map((device) => device.id)
      })
    } catch (error) {
      this.setData({ errorText: error.message || '设备加载失败' })
    } finally {
      this.setData({ isLoadingDevices: false })
    }
  },

  onTitleInput(event) {
    this.setData({ title: event.detail.value })
  },

  onContentInput(event) {
    this.setData({ content: event.detail.value })
  },

  onLevelChange(event) {
    this.setData({ levelIndex: Number(event.detail.value) })
  },

  onDurationChange(event) {
    this.setData({ durationIndex: Number(event.detail.value) })
  },

  onDeviceSelectionChange(event) {
    this.setData({ selectedDeviceIds: event.detail.value })
  },

  async submit() {
    const { title, content, levels, levelIndex, selectedDeviceIds, isSubmitting } = this.data
    if (isSubmitting) {
      return
    }

    if (!selectedDeviceIds.length) {
      wx.showToast({ title: '请至少选择一台在线设备', icon: 'none' })
      return
    }

    if (!title.trim() || !content.trim()) {
      wx.showToast({ title: '标题和正文不能为空', icon: 'none' })
      return
    }

    const app = getApp()
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isSubmitting: true })

    try {
      const result = await notificationService.sendNotification({
        title: title.trim(),
        content: content.trim(),
        level: levels[levelIndex],
        deviceIds: selectedDeviceIds,
        durationSeconds: [10, 30, 60, 0][this.data.durationIndex]
      })

      wx.showToast({
        title: `已提交 ${result.target_count} 台设备`,
        icon: 'success'
      })
      this.setData({
        title: '',
        content: ''
      })
    } catch (error) {
      wx.showToast({
        title: error.message || '发送失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isSubmitting: false })
    }
  }
})
