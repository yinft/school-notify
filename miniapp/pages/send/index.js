const { createDeviceService } = require('../../services/device')
const { createNotificationService } = require('../../services/notification')
const { ensurePageLogin } = require('../../utils/page-auth')
const { request } = require('../../utils/request')
const { getDurationSeconds, isCustomDurationSelected, CUSTOM_DURATION_INDEX } = require('./duration')

Page({
  data: {
    levels: ['普通', '重要', '紧急'],
    durations: ['30s', '1分钟', '3分钟', '5分钟', '10分钟', '自定义时长'],
    levelIndex: 0,
    durationIndex: 0,
    customDurationValue: '',
    ttsEnabled: true,
    title: '',
    content: '',
    devices: [],
    selectedDeviceIds: [],
    selectedCount: 0,
    isSubmitting: false,
    isLoadingDevices: false,
    errorText: '',
    submitHint: '请选择至少一台在线设备，并填写完整提醒内容。',
    isSubmitDisabled: true,
    isLoginRequired: false,
    loginTipText: '',
    loginGate: null,
    isAuthorizingLogin: false
  },

  async onShow() {
    wx.setNavigationBarTitle({ title: '发送' })
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    if (!(await ensurePageLogin(this, '发送提醒'))) {
      return
    }
    this.loadDevices()
  },

  async manualLogin() {
    if (this.data.isAuthorizingLogin) {
      return
    }

    this.setData({ isAuthorizingLogin: true })
    if (await ensurePageLogin(this, '发送提醒', { manual: true })) {
      this.loadDevices()
    }
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
      const onlineDevices = devices.filter((device) => device.status === 'online').map((device) => ({ ...device, selected: false }))
      this.setData({
        devices: onlineDevices,
        selectedDeviceIds: [],
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

  onTtsSwitchChange(event) {
    this.setData({ ttsEnabled: Boolean(event.detail.value) })
  },

  toggleDevice(event) {
    const idx = event.currentTarget.dataset.index
    const key = `devices[${idx}].selected`
    const device = this.data.devices[idx]
    const nowSelected = !device.selected
    this.setData({ [key]: nowSelected })
    const selectedDeviceIds = this.data.devices.filter((d) => d.selected).map((d) => d.id)
    this.setData({ selectedDeviceIds })
    this.syncSubmitState()
  },

  selectAllDevices() {
    const devices = this.data.devices.map((device) => ({ ...device, selected: true }))
    this.setData({
      devices,
      selectedDeviceIds: devices.map((d) => d.id)
    })
    this.syncSubmitState()
  },

  clearSelectedDevices() {
    const devices = this.data.devices.map((device) => ({ ...device, selected: false }))
    this.setData({
      devices,
      selectedDeviceIds: []
    })
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
    let submitHint = '请选择至少一台在线设备，并填写完整提醒内容。'
    const requiresCustomDuration = isCustomDurationSelected(durationIndex)

    if (!selectedDeviceIds.length) {
      submitHint = '当前未选择设备，请先勾选至少一台在线设备。'
    } else if (!title.trim() || !content.trim()) {
      submitHint = '标题和正文需要完整填写后才能发送。'
    } else if (requiresCustomDuration && !customDurationValue) {
      submitHint = '请输入自定义时长，单位为秒。'
    } else if (isSubmitting) {
      submitHint = '提醒正在发送，请稍候。'
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
    const { title, content, levelIndex, selectedDeviceIds, isSubmitting, durationIndex, customDurationValue, ttsEnabled } = this.data
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
        durationSeconds: getDurationSeconds({ durationIndex, customDurationValue }),
        ttsEnabled,
        ttsRepeatCount: ttsEnabled ? (levelValues[levelIndex] === 'urgent' ? 3 : 1) : 0
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
    if (this.data.isLoginRequired) {
      wx.stopPullDownRefresh()
      return
    }

    this.loadDevices().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
