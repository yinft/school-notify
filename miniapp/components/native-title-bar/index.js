Component({
  properties: {
    title: {
      type: String,
      value: ''
    },
    showBack: {
      type: Boolean,
      value: false
    }
  },

  data: {
    navHeight: 76,
    statusBarHeight: 44,
    menuButtonTopGap: 6,
    menuButtonHeight: 32
  },

  lifetimes: {
    attached() {
      this.syncNavigationMetrics()
    }
  },

  methods: {
    handleBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        wx.navigateBack({ delta: 1 })
        return
      }

      wx.switchTab({ url: '/pages/devices/index' })
    },

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
