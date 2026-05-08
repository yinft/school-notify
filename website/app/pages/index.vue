<script setup>
import { siteContent } from '../data/site-content.js'
import { structuredData } from '../data/structured-data.js'

const codeLines = [
  { prompt: 'send', text: '一条桌面提醒', tone: 'accent' },
  { prompt: 'title', text: '值班提醒', tone: 'soft' },
  { prompt: 'target', text: '我的电脑 · 在线', tone: 'ok' },
  { prompt: 'show', text: '横幅 + 语音 + 记录', tone: 'accent' }
]

useSeoMeta({
  title: siteContent.seo.title,
  description: siteContent.seo.description,
  ogTitle: siteContent.seo.title,
  ogDescription: siteContent.seo.description,
  ogType: 'website'
})

useHead({
  script: structuredData.map((item) => ({
    type: 'application/ld+json',
    innerHTML: JSON.stringify(item)
  }))
})
</script>

<template>
  <main class="site-stage">
    <section class="hero-section">
      <div class="grid-glow" aria-hidden="true"></div>
      <nav class="nav-shell" aria-label="主导航">
        <NuxtLink class="brand-lockup" to="/">
          <img src="/images/app-icon.png" alt="" aria-hidden="true" />
          <span>{{ siteContent.brand }}</span>
        </NuxtLink>
        <div class="nav-links">
          <a href="#features">功能</a>
          <a href="#download">下载</a>
          <a href="#faq">FAQ</a>
        </div>
      </nav>

      <div class="hero-grid page-shell">
        <div class="hero-copy reveal-up">
          <p class="eyebrow">{{ siteContent.hero.eyebrow }}</p>
          <h1>{{ siteContent.hero.title }}</h1>
          <p class="hero-subtitle">{{ siteContent.hero.subtitle }}</p>
          <p class="hero-description">{{ siteContent.hero.description }}</p>
          <div class="hero-actions">
            <a class="button primary" :href="siteContent.hero.actions[0].href">{{ siteContent.hero.actions[0].label }}</a>
            <a class="button secondary" :href="siteContent.hero.actions[1].href">{{ siteContent.hero.actions[1].label }}</a>
          </div>
          <dl class="hero-stats" aria-label="工具特点">
            <div v-for="stat in siteContent.hero.stats" :key="stat.label">
              <dt>{{ stat.value }}</dt>
              <dd>{{ stat.label }}</dd>
            </div>
          </dl>
        </div>

        <div class="hero-console reveal-up" aria-label="桌面小喇叭推送演示">
          <div class="orbit-card orbit-card-a">
            <span>WeChat Mini App</span>
            <strong>发送提醒</strong>
          </div>
          <div class="orbit-card orbit-card-b">
            <span>Windows Client</span>
            <strong>实时展示</strong>
          </div>

          <div class="terminal-card">
            <div class="terminal-topbar">
              <span></span><span></span><span></span>
              <small>desktop-speaker.note</small>
            </div>
            <div class="terminal-lines">
              <p v-for="(line, index) in codeLines" :key="line.prompt" :class="`line-${line.tone}`" :style="{ '--line-index': index }">
                <span>{{ line.prompt }}</span>
                <code>{{ line.text }}</code>
              </p>
            </div>
            <div class="terminal-pulse">
              <i></i><i></i><i></i>
            </div>
          </div>

          <div class="desktop-preview">
            <div class="preview-header">
              <img src="/images/app-icon.png" alt="桌面小喇叭图标" />
              <div>
                <strong>桌面小喇叭</strong>
                <span>提醒已送达 · 正在播报</span>
              </div>
            </div>
            <div class="banner-alert" aria-label="电脑端滚动提醒">
              <span>通知 · 请及时查看办公室电脑上的提醒内容</span>
            </div>
            <div class="preview-metrics">
              <b>online</b>
              <b>voice</b>
              <b>receipt</b>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="feature-section page-shell" data-aos="fade-up">
      <div class="section-heading" data-aos="fade-right" data-aos-delay="80">
        <p class="eyebrow dark">清晰的发送链路</p>
        <h2>像发一条消息一样，把提醒送到电脑桌面</h2>
      </div>
      <div class="flow-grid">
        <article v-for="(item, index) in siteContent.flow" :key="item.title" class="glass-card flow-card" data-aos="zoom-in-up" :data-aos-delay="index * 90">
          <span class="card-index">0{{ index + 1 }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </section>

    <section class="steps-section page-shell" data-aos="fade-up">
      <div class="section-heading compact" data-aos="fade-right">
        <p class="eyebrow dark">快速开始</p>
        <h2>3 步开始试用，不需要复杂配置</h2>
      </div>
      <div class="steps-grid">
        <article v-for="(step, index) in siteContent.steps" :key="step.title" class="glass-card step-card" data-aos="fade-up" :data-aos-delay="index * 120">
          <span>{{ step.number }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </article>
      </div>
    </section>

    <section class="scenarios-section page-shell" data-aos="fade-up">
      <div class="section-heading compact" data-aos="fade-right">
        <p class="eyebrow dark">使用场景</p>
        <h2>个人电脑、固定电脑都能变成提醒终端</h2>
      </div>
      <div class="scenario-grid">
        <article v-for="(scenario, index) in siteContent.scenarios" :key="scenario.title" class="glass-card scenario-card" :data-aos="index % 2 === 0 ? 'fade-right' : 'fade-left'" :data-aos-delay="index * 70">
          <h3>{{ scenario.title }}</h3>
          <p>{{ scenario.text }}</p>
        </article>
      </div>
    </section>

    <section id="download" class="download-band page-shell" data-aos="zoom-in-up">
      <img class="download-icon" src="/images/app-icon.png" alt="桌面小喇叭客户端图标" />
      <div data-aos="fade-right" data-aos-delay="120">
        <p class="eyebrow dark">下载与小程序</p>
        <h2>下载小工具，扫码绑定，然后开始发送提醒</h2>
        <p>当前版本 {{ siteContent.download.version }}，适合先在固定电脑或电脑大屏上小范围试用。</p>
      </div>
      <div class="download-actions" data-aos="fade-left" data-aos-delay="180">
        <a class="button primary light" :href="siteContent.download.href" download>下载个人试用版</a>
        <a id="miniapp" class="button secondary light" href="#miniapp-card">查看小程序说明</a>
      </div>
    </section>

    <section id="miniapp-card" class="miniapp-band page-shell" data-aos="fade-up">
      <div data-aos="fade-right" data-aos-delay="80">
        <p class="eyebrow dark">{{ siteContent.miniapp.status }}</p>
        <h2>扫码绑定设备，再发送提醒</h2>
        <p>{{ siteContent.miniapp.note }}</p>
      </div>
      <div class="qr-placeholder" aria-label="小程序码占位" data-aos="flip-left" data-aos-delay="160">
        <span>小程序码</span>
        <small>上线后替换</small>
      </div>
    </section>

    <section id="faq" class="faq-section page-shell" data-aos="fade-up">
      <div class="section-heading compact" data-aos="fade-right">
        <p class="eyebrow dark">FAQ</p>
        <h2>常见问题</h2>
      </div>
      <div class="faq-list">
        <article v-for="(item, index) in siteContent.faq" :key="item.question" class="glass-card" data-aos="fade-up" :data-aos-delay="index * 80">
          <h3>{{ item.question }}</h3>
          <p>{{ item.answer }}</p>
        </article>
      </div>
    </section>
  </main>
</template>
