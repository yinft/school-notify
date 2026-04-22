const { createDeviceService } = require('../../services/device')
const { createNotificationService } = require('../../services/notification')
const { request } = require('../../utils/request')
const { getDurationSeconds, isCustomDurationSelected, CUSTOM_DURATION_INDEX } = require('./duration')

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
    levels: ['普通', '重要', '紧急'],
    durations: ['30s', '1分钟', '3分钟', '5分钟', '10分钟', '自定义时长'],
    levelIndex: 0,
    durationIndex: 0,
    customDurationValue: '',
    title: '',
    content: '',
    devices: [],
    selectedDeviceIds: [],
    selectedCount: 0,
    isSubmitting: false,
    isLoadingDevices: false,
    errorText: '',
    submitHint: '请选择至少一台在线设备，并填写完整通知内容。',
    isSubmitDisabled: true
  },

  onShow() {
    if (!checkAuth()) return
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
        selectedDeviceIds: onlineDevices.map((device) => device.id),
        errorText: ''
      })
      this.syncSubmitState()
    } catch (error) {
      this.setData({
        errorText: error.message || '设备加载失败',
        devices: [],
        selectedDeviceIds: []
      })
      this.syncSubmitState()
    } finally {
      this.setData({ isLoadingDevices: false })
    }
  },

  onTitleInput(event) {
    this.setData({ title: event.detail.value })
    this.syncSubmitState()
  },

  onContentInput(event) {
    this.setData({ content: event.detail.value })
    this.syncSubmitState()
  },

  onLevelChange(event) {
    this.setData({ levelIndex: Number(event.detail.value) })
  },

  onDurationChange(event) {
    this.setData({ durationIndex: Number(event.detail.value) })
    this.syncSubmitState()
  },

  onCustomDurationInput(event) {
    this.setData({ customDurationValue: event.detail.value.replace(/[^\d]/g, '') })
    this.syncSubmitState()
  },

  onDeviceSelectionChange(event) {
    this.setData({ selectedDeviceIds: event.detail.value })
    this.syncSubmitState()
  },

  selectAllDevices() {
    this.setData({
      selectedDeviceIds: this.data.devices.map((device) => device.id)
    })
    this.syncSubmitState()
  },

  clearSelectedDevices() {
    this.setData({ selectedDeviceIds: [] })
    this.syncSubmitState()
  },

  goToDevices() {
    wx.switchTab({ url: '/pages/devices/index' })
  },

  goToBind() {
    wx.navigateTo({ url: '/pages/bind/index' })
  },

  syncSubmitState() {
    const { title, content, selectedDeviceIds, isSubmitting, durationIndex, customDurationValue } = this.data
    let submitHint = '请选择至少一台在线设备，并填写完整通知内容。'
    const requiresCustomDuration = isCustomDurationSelected(durationIndex)

    if (!selectedDeviceIds.length) {
      submitHint = '当前未选择设备，请先勾选至少一台在线设备。'
    } else if (!title.trim() || !content.trim()) {
      submitHint = '标题和正文需要完整填写后才能发送。'
    } else if (requiresCustomDuration && !customDurationValue) {
      submitHint = '请输入自定义时长，单位为秒。'
    } else if (isSubmitting) {
      submitHint = '通知正在发送，请稍候。'
    } else {
      submitHint = `本次将发送到 ${selectedDeviceIds.length} 台在线设备。`
    }

    this.setData({
      selectedCount: selectedDeviceIds.length,
      isSubmitDisabled:
        isSubmitting ||
        !selectedDeviceIds.length ||
        !title.trim() ||
        !content.trim() ||
        (requiresCustomDuration && !customDurationValue),
      submitHint
    })
  },

  async submit() {
    const { title, content, levelIndex, selectedDeviceIds, isSubmitting, durationIndex, customDurationValue } = this.data
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

    if (isCustomDurationSelected(durationIndex) && !customDurationValue) {
      wx.showToast({ title: '请输入自定义时长', icon: 'none' })
      return
    }

    const app = getApp()
    const levelValues = ['normal', 'important', 'urgent']
    const notificationService = createNotificationService({
      request,
      currentUserId: app.globalData.currentUserId
    })

    this.setData({ isSubmitting: true })
    this.syncSubmitState()

    try {
      const result = await notificationService.sendNotification({
        title: title.trim(),
        content: content.trim(),
        level: levelValues[levelIndex],
        deviceIds: selectedDeviceIds,
        durationSeconds: getDurationSeconds({ durationIndex, customDurationValue })
      })

      wx.showToast({
        title: `已提交 ${result.target_count} 台设备`,
        icon: 'success'
      })
      this.setData({
        title: '',
        content: '',
        customDurationValue: '',
        durationIndex: 0
      })
      this.syncSubmitState()
    } catch (error) {
      wx.showToast({
        title: error.message || '发送失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isSubmitting: false })
      this.syncSubmitState()
    }
  },

  onPullDownRefresh() {
    this.loadDevices().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
