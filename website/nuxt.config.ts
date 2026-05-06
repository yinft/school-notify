export default defineNuxtConfig({
  compatibilityDate: '2026-05-06',
  css: ['aos/dist/aos.css', '~/assets/css/main.css'],
  modules: ['@nuxtjs/seo'],
  app: {
    head: {
      htmlAttrs: { lang: 'zh-CN' },
      link: [{ rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }]
    }
  },
  site: {
    url: 'https://www.shcoolhelper.cn',
    name: '桌面提醒小喇叭',
    description: '用微信小程序向 Windows 电脑发送横幅、卡片和语音提醒。'
  },
  nitro: {
    prerender: {
      routes: ['/']
    }
  }
})
