Component({
  data: {
    selected: 0,
    list: [
      { pagePath: '/pages/devices/index', text: '设备', icon: 'devices' },
      { pagePath: '/pages/send/index', text: '发送', icon: 'send' },
      { pagePath: '/pages/records/index', text: '记录', icon: 'records' },
      { pagePath: '/pages/profile/index', text: '我的', icon: 'profile' }
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
