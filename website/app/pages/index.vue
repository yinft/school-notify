<script setup>
import { siteContent } from '../data/site-content.js'
import { structuredData } from '../data/structured-data.js'

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
  <main>
    <section class="hero-section">
      <nav class="nav-shell" aria-label="主导航">
        <NuxtLink class="brand" to="/">{{ siteContent.brand }}</NuxtLink>
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
          <dl class="hero-stats">
            <div v-for="stat in siteContent.hero.stats" :key="stat.label">
              <dt>{{ stat.value }}</dt>
              <dd>{{ stat.label }}</dd>
            </div>
          </dl>
        </div>

        <div class="product-demo reveal-up" aria-label="产品流程演示">
          <div class="phone-card">
            <span>微信小程序</span>
            <strong>通知</strong>
            <p>请xxx来一趟办公室/值班室。</p>
            <button>发送到 Windows 电脑</button>
          </div>
          <div class="signal-line"></div>
          <div class="desktop-card">
            <div class="desktop-topbar"></div>
            <div class="banner-alert" aria-label="通知：请xxx来一趟办公室/值班室">
              <span>通知 · 请xxx来一趟办公室/值班室</span>
            </div>
            <div class="receipt-pill">已送达 · 正在语音播报</div>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="light-section page-shell" data-aos="fade-up">
      <div class="section-heading" data-aos="fade-right" data-aos-delay="80">
        <p class="eyebrow dark">清晰的发送链路</p>
        <h2>从小程序到电脑提醒，只保留必要步骤</h2>
      </div>
      <div class="flow-grid">
        <article v-for="(item, index) in siteContent.flow" :key="item.title" class="flow-card" data-aos="zoom-in-up" :data-aos-delay="index * 90">
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </section>

    <section class="steps-section page-shell" data-aos="fade-up">
      <div class="section-heading compact" data-aos="fade-right">
        <h2>3 步开始使用</h2>
      </div>
      <div class="steps-grid">
        <article v-for="(step, index) in siteContent.steps" :key="step.title" class="step-card" data-aos="fade-up" :data-aos-delay="index * 120">
          <span>{{ step.number }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </article>
      </div>
    </section>

    <section class="scenarios-section page-shell" data-aos="fade-up">
      <div class="section-heading compact" data-aos="fade-right">
        <h2>适合固定电脑和公共屏的提醒场景</h2>
      </div>
      <div class="scenario-grid">
        <article v-for="(scenario, index) in siteContent.scenarios" :key="scenario.title" class="scenario-card" :data-aos="index % 2 === 0 ? 'fade-right' : 'fade-left'" :data-aos-delay="index * 70">
          <h3>{{ scenario.title }}</h3>
          <p>{{ scenario.text }}</p>
        </article>
      </div>
    </section>

    <section id="download" class="download-band page-shell" data-aos="zoom-in-up">
      <div data-aos="fade-right" data-aos-delay="120">
        <p class="eyebrow dark">下载与小程序</p>
        <h2>一个页面完成下载、绑定和说明</h2>
        <p>下载 Windows 客户端，在小程序里绑定设备后即可发送提醒。</p>
      </div>
      <div class="download-actions" data-aos="fade-left" data-aos-delay="180">
        <a class="button primary light" :href="siteContent.download.href" download>下载客户端</a>
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
        <h2>常见问题</h2>
      </div>
      <div class="faq-list">
        <article v-for="(item, index) in siteContent.faq" :key="item.question" data-aos="fade-up" :data-aos-delay="index * 80">
          <h3>{{ item.question }}</h3>
          <p>{{ item.answer }}</p>
        </article>
      </div>
    </section>
  </main>
</template>
