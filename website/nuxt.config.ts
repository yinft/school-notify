import { defaultSiteUrl } from './app/data/site-config.js'

const defaultBackendBaseUrl = process.env.NODE_ENV === 'production'
  ? 'https://admin.schoolhelper.cn'
  : 'http://127.0.0.1:8000'

export default defineNuxtConfig({
  compatibilityDate: '2026-05-06',
  css: ['aos/dist/aos.css', '~/assets/css/main.css'],
  modules: ['@nuxtjs/seo'],
  app: {
    head: {
      htmlAttrs: { lang: 'zh-CN' },
      link: [
        { rel: 'icon', href: '/favicon.ico', sizes: 'any' },
        { rel: 'icon', href: '/images/app-icon.png', type: 'image/png' }
      ]
    }
  },
  runtimeConfig: {
    public: {
      backendBaseUrl: process.env.NUXT_PUBLIC_BACKEND_BASE_URL || defaultBackendBaseUrl,
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || defaultSiteUrl
    }
  },
  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || defaultSiteUrl,
    name: '思故桌面小喇叭',
    description: '用微信小程序向 Windows 电脑发送横幅、卡片和语音提醒。'
  },
  sitemap: {
    zeroRuntime: true
  },
  ogImage: {
    zeroRuntime: true
  },
  nitro: {
    prerender: {
      routes: ['/']
    }
  }
})
