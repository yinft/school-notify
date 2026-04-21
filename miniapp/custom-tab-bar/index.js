Component({
  data: {
    selected: 0,
    list: [
      { pagePath: '/pages/devices/index', text: '设备', icon: '💻' },
      { pagePath: '/pages/send/index', text: '发送', icon: '📨' },
      { pagePath: '/pages/records/index', text: '记录', icon: '📋' },
      { pagePath: '/pages/profile/index', text: '我的', icon: '👤' }
    ]
  },

  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      wx.switchTab({ url })
    }
  }
})
