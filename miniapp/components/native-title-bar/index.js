Component({
  properties: {
    title: {
      type: String,
      value: ''
    }
  },

  data: {
    navHeight: 0,
    statusBarHeight: 0,
    menuButtonTopGap: 0,
    menuButtonHeight: 32
  },

  lifetimes: {
    attached() {
      this.syncNavigationMetrics()
    }
  },

  methods: {
    syncNavigationMetrics() {
      const systemInfo = wx.getSystemInfoSync ? wx.getSystemInfoSync() : {}
      const menuButton = wx.getMenuButtonBoundingClientRect ? wx.getMenuButtonBoundingClientRect() : null
      const statusBarHeight = systemInfo.statusBarHeight || 44

      if (!menuButton) {
        this.setData({ statusBarHeight })
        return
      }

      const menuButtonHeight = menuButton.height || 32
      const menuButtonTopGap = Math.max(menuButton.top - statusBarHeight, 0)
      const navHeight = menuButton.bottom
      this.setData({
        navHeight,
        statusBarHeight,
        menuButtonTopGap,
        menuButtonHeight
      })
    }
  }
})
