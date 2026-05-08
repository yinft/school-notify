export const siteContent = {
  brand: '思故桌面小喇叭',
  seo: {
    title: '思故桌面小喇叭 - 桌面小喇叭工具介绍',
    description: '思故桌面小喇叭是个人开发的桌面小喇叭工具，用微信小程序把简短提醒发送到自己的 Windows 电脑，适合个人学习、小范围试用和固定电脑提醒场景。',
    keywords: ['个人工具', '桌面提醒小工具', 'Windows 桌面提醒', '电脑提醒', '语音播报提醒']
  },
  hero: {
    eyebrow: '个人工具 · 免费试用',
    title: '思故桌面小喇叭',
    subtitle: '一个个人开发的桌面提醒小工具',
    description: '用微信小程序给自己的 Windows 电脑发送简短提醒，电脑端可以显示横幅、卡片和语音播报。本页用于介绍桌面小喇叭工具的用途、下载方式和基本使用流程。',
    actions: [
      { label: '下载个人试用版', href: '#download' },
      { label: '查看微信小程序', href: '#miniapp' }
    ],
    stats: [
      { value: '3 步', label: '下载、绑定、试用' },
      { value: '轻量', label: '固定电脑提醒' },
      { value: '免费', label: '个人小范围试用' }
    ]
  },
  flow: [
    { title: '小程序填写', text: '在微信小程序里填写简短提醒，选择自己已经绑定的电脑。' },
    { title: '发送到电脑', text: '提醒内容会发送到在线的 Windows 端，用于个人或小范围提醒。' },
    { title: '桌面展示', text: '电脑端显示横幅、短卡片和语音播报，帮助减少遗漏。' },
    { title: '记录可查', text: '发送后可以查看简单记录，确认提醒是否已经到达。' }
  ],
  steps: [
    { number: '01', title: '下载小工具', text: '在自己的 Windows 电脑上下载并打开桌面端小工具。' },
    { number: '02', title: '扫码绑定', text: '用微信小程序扫描桌面端二维码，完成设备绑定。' },
    { number: '03', title: '发送提醒', text: '在小程序里输入标题和正文，电脑端会弹出提醒。' }
  ],
  scenarios: [
    { title: '个人电脑提醒', text: '在手机上写一条提醒，让自己的电脑桌面及时显示。' },
    { title: '固定电脑提示', text: '适合放在常用电脑、备用电脑或固定显示设备上做轻量提示。' },
    { title: '值守场景提醒', text: '适合需要临时提示的值守电脑，减少口头转达和遗漏。' },
    { title: '小范围试用', text: '适合个人学习、家庭或小团队内部试用，不作为经营性项目。' }
  ],
  features: [
    '微信小程序发送',
    'Windows 横幅提醒',
    '语音播报',
    '设备在线状态',
    '扫码绑定设备',
    '发送记录查看'
  ],
  download: {
    version: '0.1.0',
    updatedAt: '2026-05-06',
    fileName: 'desktop-speaker-windowsclient-green-self-contained-win-x64.zip',
    href: '/downloads/desktop-speaker-windowsclient-green-self-contained-win-x64.zip',
    checksum: '发布前填写 SHA256 校验值'
  },
  miniapp: {
    status: '微信小程序入口',
    note: '上线后在这里放置小程序码。当前页面用于说明个人工具的绑定和使用流程。'
  },
  compliance: [
    '本页为个人开发桌面小喇叭工具的介绍与使用说明页面，不提供经营性项目。',
    '思故桌面小喇叭仅用于个人学习和小范围试用。',
    '不需要上传通讯录、人员名单或联系方式。',
    '通知内容仅用于发送到已绑定设备，请勿填写敏感个人信息。',
    '如果后续使用范围或网站主体发生变化，应重新评估备案和合规要求。'
  ],
  faq: [
    { question: '这个工具免费吗？', answer: '前期免费，定位是个人开发的小工具，不提供收费套餐。' },
    { question: '会收集敏感信息吗？', answer: '不会。工具不设计通讯录、人员档案或联系方式上传功能，也建议不要在通知正文里填写敏感信息。' },
    { question: '支持哪些 Windows 电脑？', answer: '目标是支持常见 Windows 桌面环境，适合需要常驻提醒的固定电脑。' },
    { question: '适合哪些使用场景？', answer: '适合个人电脑、固定电脑、家庭或小范围内部试用等轻量提醒场景。' },
    { question: '需要统一部署吗？', answer: '不需要。下载小工具、扫码绑定后即可小范围试用。' }
  ]
}
