export const siteContent = {
  brand: '桌面提醒小喇叭',
  seo: {
    title: '桌面提醒小喇叭 - 微信小程序发送 Windows 桌面提醒',
    description: '个人开发的免费提醒工具，用微信小程序向 Windows 电脑、固定电脑和电脑大屏发送横幅、卡片和语音提醒，适合办公室、值班室、会议室、机房等公共屏场景。',
    keywords: ['微信小程序发送电脑通知', 'Windows 桌面提醒', '电脑大屏提醒', '公共屏通知', '桌面横幅通知', '语音播报提醒']
  },
  hero: {
    eyebrow: '个人开发 · 前期免费开放',
    title: '桌面提醒小喇叭',
    subtitle: '把消息发送到电脑桌面',
    description: '用微信小程序发送消息，Windows 电脑实时弹出横幅、卡片和语音播报。支持多人扫码绑定、在线状态、发送记录，让办公室、值班室、会议室、机房等固定电脑或电脑大屏变成醒目的提醒屏。',
    actions: [
      { label: '免费下载 Windows 客户端', href: '#download' },
      { label: '查看微信小程序', href: '#miniapp' }
    ],
    stats: [
      { value: '3 步', label: '下载、绑定、发送' },
      { value: '实时', label: '在线设备秒级提醒' },
      { value: '免费', label: '前期免费开放使用' }
    ]
  },
  flow: [
    { title: '小程序发送', text: '在微信小程序里填写提醒内容，选择已绑定的电脑设备。' },
    { title: '实时推送', text: '后端保持设备在线状态，只向在线 Windows 客户端推送提醒。' },
    { title: '电脑醒目展示', text: '桌面端显示顶部横幅、短卡片和语音播报，减少错过消息。' },
    { title: '送达可见', text: '发送后能看到设备投递状态，知道提醒是否已经到达。' }
  ],
  steps: [
    { number: '01', title: '下载客户端', text: '在需要常驻提醒的 Windows 电脑上下载并打开客户端。' },
    { number: '02', title: '扫码绑定', text: '用微信小程序扫描客户端里的二维码，完成设备绑定。' },
    { number: '03', title: '发送提醒', text: '在小程序里输入标题和正文，电脑端会立即弹出醒目提醒。' }
  ],
  scenarios: [
    { title: '办公室到大屏提醒', text: '在办公室发送消息，让远端固定电脑或电脑大屏立即显示横幅提醒。' },
    { title: '公共屏提示', text: '适合把文字提醒展示到公共屏、前台屏、公告屏等固定屏幕。' },
    { title: '值班通知', text: '适合值班室、办公室、门卫室等共享电脑的临时通知。' },
    { title: '会议室与机房', text: '让会议室、机房、实验室等固定电脑变成轻量提醒屏，减少口头转达和遗漏。' }
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
    fileName: 'schoolnotify-windowsclient-green-self-contained-win-x64.zip',
    href: '/downloads/schoolnotify-windowsclient-green-self-contained-win-x64.zip',
    checksum: '发布前填写 SHA256 校验值'
  },
  miniapp: {
    status: '微信小程序入口',
    note: '上线后在这里放置小程序码。当前页面先用于说明绑定和使用流程。'
  },
  compliance: [
    '个人开发的免费工具，前期免费开放使用。',
    '不需要上传通讯录、人员名单或联系方式。',
    '通知内容仅用于发送到已绑定设备，请勿填写敏感个人信息。',
    '如果后续使用范围或服务主体发生变化，应重新评估备案和合规要求。'
  ],
  faq: [
    { question: '这个工具免费吗？', answer: '前期完全免费，定位是个人开发的小工具，不提供收费套餐。' },
    { question: '会收集敏感信息吗？', answer: '不会。产品不设计通讯录、人员档案或联系方式上传功能，也建议不要在通知正文里填写敏感信息。' },
    { question: '支持哪些 Windows 电脑？', answer: '目标是支持常见 Windows 桌面环境，适合需要常驻提醒的固定电脑。' },
    { question: '适合哪些固定屏幕场景？', answer: '适合办公室、值班室、会议室、机房、门卫室等需要把消息展示到固定电脑或电脑大屏的场景。' },
    { question: '需要统一部署吗？', answer: '不需要。下载客户端、扫码绑定后即可小范围试用。' }
  ]
}
