import assert from 'node:assert/strict'
import test from 'node:test'

import { siteContent } from '../app/data/site-content.js'
import { structuredData } from '../app/data/structured-data.js'

test('homepage positions the product around notification features', () => {
  assert.equal(siteContent.brand, '桌面提醒小喇叭')
  assert.match(siteContent.hero.eyebrow, /免费/)
  assert.equal(siteContent.hero.title, '桌面提醒小喇叭')
  assert.match(siteContent.hero.subtitle, /消息发送到电脑桌面/)
  assert.match(siteContent.hero.description, /微信小程序/)
  assert.match(siteContent.hero.description, /Windows/)
})

test('primary actions use same-page anchors', () => {
  assert.equal(siteContent.hero.actions[0].label, '免费下载 Windows 客户端')
  assert.equal(siteContent.hero.actions[0].href, '#download')
  assert.equal(siteContent.hero.actions[1].label, '查看微信小程序')
  assert.equal(siteContent.hero.actions[1].href, '#miniapp')
})

test('copy avoids audience-specific and platform positioning', () => {
  const combinedCopy = JSON.stringify(siteContent)

  assert.doesNotMatch(combinedCopy, /学生|老师|教师|校园|学校|班级|家长|教育 SaaS|学校通知平台|企业级部署|授权购买|商业合作/)
  assert.match(combinedCopy, /个人开发/)
  assert.match(combinedCopy, /不需要上传通讯录/)
})

test('seo faq covers free use, privacy, and windows support', () => {
  const questions = siteContent.faq.map((item) => item.question).join('\n')

  assert.match(questions, /免费/)
  assert.match(questions, /敏感信息/)
  assert.match(questions, /Windows/)
})

test('scenario copy covers generic fixed-screen use cases', () => {
  const scenarioCopy = [
    siteContent.seo.description,
    siteContent.hero.description,
    ...siteContent.scenarios.map((item) => `${item.title}${item.text}`),
    ...siteContent.faq.map((item) => `${item.question}${item.answer}`)
  ].join('\n')

  assert.match(scenarioCopy, /办公室/)
  assert.match(scenarioCopy, /固定电脑/)
  assert.match(scenarioCopy, /电脑大屏|公共屏/)
  assert.match(scenarioCopy, /值班室/)
  assert.match(scenarioCopy, /会议室/)
  assert.match(scenarioCopy, /机房/)
})

test('structured data describes the app and faq without restricted positioning', () => {
  const software = structuredData.find((item) => item['@type'] === 'SoftwareApplication')
  const faq = structuredData.find((item) => item['@type'] === 'FAQPage')
  const combinedStructuredData = JSON.stringify(structuredData)

  assert.equal(software.name, siteContent.brand)
  assert.equal(software.operatingSystem, 'Windows')
  assert.equal(software.applicationCategory, 'UtilitiesApplication')
  assert.equal(faq.mainEntity.length, siteContent.faq.length)
  assert.doesNotMatch(combinedStructuredData, /学生|老师|教师|教室|校园|学校|班级|家长|教育 SaaS|学校通知平台|企业级部署|授权购买|商业合作/)
})
