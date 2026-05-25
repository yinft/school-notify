const test = require('node:test')
const assert = require('node:assert/strict')

const { createDeviceService, formatLastSeenText } = require('../services/device')
const { createBindingService, extractBindCodeFromScan, getBindingErrorMessage, normalizeBindCode } = require('../services/binding')
const { createNotificationService } = require('../services/notification')
const { createAuthService } = require('../services/auth')
const { getDurationSeconds, isCustomDurationSelected } = require('../pages/send/duration')
const { createLoginGateModel } = require('../utils/login-gate')
const { buildRequestOptions, getErrorMessage } = require('../utils/request')
const { createUserProfile, hasAuthorizedProfile, uploadAvatarToQiniu, syncWechatProfile } = require('../utils/user-profile')
const fs = require('node:fs')
const path = require('node:path')
const {
  DEFAULT_USER_ID,
  createLoggedInSession,
  createLoggedOutSession,
  hasLoginSession,
  shouldAutoLogin,
  getLoginRequiredMessage
} = require('../utils/auth-session')

test('formatLastSeenText formats missing timestamps', () => {
  assert.equal(formatLastSeenText(null), '暂无在线记录')
})

test('miniapp uses custom bottom tab bar with page-selected state sync', () => {
  const appConfig = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../app.json'), 'utf8'))
  const tabbedPageScripts = [
    fs.readFileSync(path.resolve(__dirname, '../pages/devices/index.js'), 'utf8'),
    fs.readFileSync(path.resolve(__dirname, '../pages/send/index.js'), 'utf8'),
    fs.readFileSync(path.resolve(__dirname, '../pages/records/index.js'), 'utf8'),
    fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')
  ]

  assert.equal(appConfig.tabBar.custom, true)
  assert.equal(appConfig.tabBar.list.length, 4)
  assert.equal(tabbedPageScripts.every((script) => script.includes('getTabBar')), true)
})

test('miniapp uses native navigation to avoid first tab page layout jump', () => {
  const appConfig = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../app.json'), 'utf8'))
  const pageMarkups = ['devices', 'bind', 'send', 'records', 'profile'].map((page) =>
    fs.readFileSync(path.resolve(__dirname, `../pages/${page}/index.wxml`), 'utf8')
  )

  assert.notEqual(appConfig.window.navigationStyle, 'custom')
  assert.equal(Boolean(appConfig.usingComponents && appConfig.usingComponents['native-title-bar']), false)
  assert.equal(pageMarkups.some((markup) => markup.includes('<native-title-bar')), false)
})

test('tab pages start in loading state to avoid first-entry empty-state flicker', () => {
  const sendScript = fs.readFileSync(path.resolve(__dirname, '../pages/send/index.js'), 'utf8')
  const recordsScript = fs.readFileSync(path.resolve(__dirname, '../pages/records/index.js'), 'utf8')
  const profileScript = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')
  const sendInitialData = sendScript.match(/data:\s*\{[\s\S]*?\n  \},/)?.[0] || ''
  const recordsInitialData = recordsScript.match(/data:\s*\{[\s\S]*?\n  \},/)?.[0] || ''
  const profileInitialData = profileScript.match(/data:\s*\{[\s\S]*?\n  \},/)?.[0] || ''

  assert.match(sendInitialData, /isLoadingDevices:\s*true/)
  assert.match(recordsInitialData, /isLoading:\s*true/)
  assert.match(profileInitialData, /isProfileReady:\s*false/)
  assert.match(profileMarkup, /wx:elif="\{\{!isProfileReady\}\}"/)
})

test('profile page avoids empty overscroll when content fits the viewport', () => {
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')
  const profileStyle = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxss'), 'utf8')

  assert.match(profileMarkup, /class="page-body profile-page-body"/)
  assert.match(profileStyle, /\.profile-page-body\s*\{[\s\S]*overflow-y:\s*auto;/)
  assert.match(profileStyle, /\.profile-page-body\s*\{[\s\S]*padding-bottom:\s*calc\(24rpx \+ env\(safe-area-inset-bottom\)\);/)
})

test('profile page sets native navigation title when shown', () => {
  const profileScript = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')

  assert.match(profileScript, /wx\.setNavigationBarTitle\(\{\s*title:\s*'我的'\s*\}\)/)
})

test('device list uses simple separators without alternating left accent bars', () => {
  const devicesStyle = fs.readFileSync(path.resolve(__dirname, '../pages/devices/index.wxss'), 'utf8')

  assert.match(devicesStyle, /\.device-row\s*\{[\s\S]*border-bottom:\s*1rpx solid #edf4ff;/)
  assert.doesNotMatch(devicesStyle, /\.device-row:nth-child/)
  assert.doesNotMatch(devicesStyle, /border-left/)
})

test('profile nickname uses wechat nickname input type with auto-save on blur', () => {
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')
  const profileStyle = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxss'), 'utf8')
  const profileScript = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')

  assert.match(profileMarkup, /class="profile-nick-field"/)
  assert.match(profileMarkup, /input[\s\S]*class="profile-nick-input"[\s\S]*bindblur="onNickNameConfirm"/)
  assert.match(profileMarkup, /bindconfirm="onNickNameConfirm"/)
  assert.match(profileMarkup, /type="nickname"/)
  assert.doesNotMatch(profileMarkup, /class="profile-nick-sync-trigger"/)
  assert.match(profileStyle, /\.profile-nick-field\s*\{/)
  assert.match(profileStyle, /\.profile-nick-input\s*\{[\s\S]*color:\s*#ffffff;/)
  assert.match(profileStyle, /\.profile-nick-input\s*\{[\s\S]*background:\s*transparent;/)
  assert.match(profileScript, /onNickNameConfirm\(event\)/)
})

test('profile nickname input has no value binding so WeChat nickname selection is not overridden', () => {
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')
  const profileScript = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')
  const profileStyle = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxss'), 'utf8')

  assert.doesNotMatch(profileMarkup, /value="\{\{/)
  assert.doesNotMatch(profileMarkup, /bindinput="onNickNameInput"/)
  assert.match(profileMarkup, /placeholder="\{\{nickNamePlaceholder\}\}"/)
  assert.match(profileStyle, /\.profile-nick-placeholder\s*\{[^}]*color:\s*#ffffff/)
  assert.match(profileScript, /nickNamePlaceholder:\s*''/)
  assert.match(profileScript, /nickNamePlaceholder:\s*profile\.nickName/)
})

test('records page initial load is not blocked by the loading guard', () => {
  const recordsScript = fs.readFileSync(path.resolve(__dirname, '../pages/records/index.js'), 'utf8')

  assert.match(recordsScript, /hasLoadedOnce:\s*false/)
  assert.match(recordsScript, /\(!append && this\.data\.isLoading && this\.data\.hasLoadedOnce\)/)
  assert.match(recordsScript, /hasLoadedOnce:\s*true/)
})

test('records page uses scroll-view with scrolltolower for infinite loading', () => {
  const recordsMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/records/index.wxml'), 'utf8')
  const recordsScript = fs.readFileSync(path.resolve(__dirname, '../pages/records/index.js'), 'utf8')

  assert.match(recordsMarkup, /scroll-view[\s\S]*scroll-y/)
  assert.match(recordsMarkup, /bindscrolltolower="onScrollToLower"/)
  assert.match(recordsScript, /onScrollToLower/)
})

test('profile nickname display stays in a single editable row', () => {
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')

  assert.match(profileMarkup, /class="profile-nick-field"/)
  assert.match(profileMarkup, /class="profile-nick-input"/)
})

test('send page keeps selected devices when device list reloads', () => {
  const sendScript = fs.readFileSync(path.resolve(__dirname, '../pages/send/index.js'), 'utf8')
  const loadDevicesBlock = sendScript.match(/async loadDevices\(\) \{[\s\S]*?\n  \},/)?.[0] || ''
  const successBranch = loadDevicesBlock.match(/const selectedDeviceIds = new Set\(this\.data\.selectedDeviceIds\)[\s\S]*?this\.syncSubmitState\(\)/)?.[0] || ''

  assert.match(successBranch, /const selectedDeviceIds = new Set\(this\.data\.selectedDeviceIds\)/)
  assert.match(successBranch, /selected: selectedDeviceIds\.has\(device\.id\)/)
  assert.match(successBranch, /selectedDeviceIds: onlineDevices\.filter\(\(device\) => device\.selected\)\.map\(\(device\) => device\.id\)/)
})

test('send page rejects non-positive custom durations', () => {
  const sendScript = fs.readFileSync(path.resolve(__dirname, '../pages/send/index.js'), 'utf8')

  assert.match(sendScript, /Number\(customDurationValue\) <= 0/)
  assert.match(sendScript, /请输入大于 0 的自定义时长/)
})

test('formatLastSeenText formats local timestamps', () => {
  assert.equal(formatLastSeenText('2026-04-21T16:00:00'), '最后在线：2026-04-21 16:00:00')
})

test('createDeviceService fetches and maps user devices', async () => {
  const calls = []
  const service = createDeviceService({
    request(options) {
      calls.push(options)
      return Promise.resolve({
        items: [
          {
            device_id: 'device-001',
            device_name: '值班室电脑',
            location_label: '会议室',
            client_version: '0.1.0',
            status: 'online',
            last_seen_at: '2026-04-21T16:00:00'
          }
        ]
      })
    },
    currentUserId: 'user-001'
  })

  const devices = await service.fetchUserDevices()

  assert.deepEqual(calls, [{ url: '/users/user-001/devices' }])
  assert.deepEqual(devices, [
    {
      id: 'device-001',
      name: '值班室电脑',
      locationLabel: '会议室',
      clientVersion: '0.1.0',
      status: 'online',
      lastSeenAt: '2026-04-21T16:00:00',
      lastSeenText: '最后在线：2026-04-21 16:00:00',
      statusText: '在线'
    }
  ])
})

test('createNotificationService sends current user id and selected devices', async () => {
  const calls = []
  const service = createNotificationService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ status: 'accepted', target_count: 2 })
    },
    currentUserId: 'user-001'
  })

  const result = await service.sendNotification({
    title: '紧急提醒',
    content: '请立即到场',
    level: 'urgent',
    deviceIds: ['device-001', 'device-002'],
    durationSeconds: 30,
    ttsEnabled: true,
    ttsRepeatCount: 3
  })

  assert.deepEqual(calls, [
    {
      url: '/notifications',
      method: 'POST',
      data: {
        sender_user_id: 'user-001',
        title: '紧急提醒',
        content: '请立即到场',
        level: 'urgent',
        device_ids: ['device-001', 'device-002'],
        duration_seconds: 30,
        tts_enabled: true,
        tts_repeat_count: 3
      }
    }
  ])
  assert.deepEqual(result, { status: 'accepted', target_count: 2 })
})

test('createNotificationService fetches and maps notification records', async () => {
  const calls = []
  const service = createNotificationService({
    request(options) {
      calls.push(options)
      return Promise.resolve({
        items: [
          {
            notification_id: 'notification-1',
            sender_user_id: 'user-001',
            title: '紧急提醒',
            content: '请立即集合',
            level: 'urgent',
            target_count: 1,
            deliveries: [
              {
                device_id: 'device-001',
                device_name: '办公室提醒屏',
                location_label: '办公室',
                received: true,
                displayed: true,
                spoken: false
              }
            ]
          }
        ],
        total: 1
      })
    },
    currentUserId: 'user-001'
  })

  const { records } = await service.fetchNotificationRecords()

  assert.deepEqual(calls, [{ url: '/notifications?sender_user_id=user-001' }])
  assert.deepEqual(records, [
    {
      id: 'notification-1',
      title: '紧急提醒',
      content: '请立即集合',
      level: 'urgent',
      targetCount: 1,
      deliverySummary: '1 台设备，1 台已展示',
      deliveries: [
        {
          deviceId: 'device-001',
          deviceName: '办公室提醒屏',
          locationLabel: '办公室',
          displayName: '办公室提醒屏',
          displayMeta: '办公室',
          received: true,
          displayed: true,
          spoken: false,
          failed: false,
          errorMessage: '',
          statusText: '已展示'
        }
      ]
    }
  ])
})

test('createNotificationService requests paged notification records', async () => {
  const calls = []
  const service = createNotificationService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ items: [], total: 25 })
    },
    currentUserId: 'user-001'
  })

  const result = await service.fetchNotificationRecords({ limit: 10, offset: 20 })

  assert.deepEqual(calls, [{ url: '/notifications?sender_user_id=user-001&limit=10&offset=20' }])
  assert.deepEqual(result, { records: [], total: 25 })
})

test('createNotificationService requests notification records within selected date range', async () => {
  const calls = []
  const service = createNotificationService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ items: [], total: 0 })
    },
    currentUserId: 'user-001'
  })

  const result = await service.fetchNotificationRecords({
    limit: 10,
    offset: 0,
    startAt: '2026-04-27T16:00:00.000Z',
    endAt: '2026-04-28T16:00:00.000Z'
  })

  assert.deepEqual(calls, [{
    url: '/notifications?sender_user_id=user-001&limit=10&offset=0&start_at=2026-04-27T16%3A00%3A00.000Z&end_at=2026-04-28T16%3A00%3A00.000Z'
  }])
  assert.deepEqual(result, { records: [], total: 0 })
})

test('createNotificationService falls back to shortened device id when device name is missing', async () => {
  const service = createNotificationService({
    request() {
      return Promise.resolve({
        items: [
          {
            notification_id: 'notification-1',
            title: '通知',
            content: '内容',
            level: 'normal',
            target_count: 1,
            deliveries: [
              {
                device_id: '1234567890abcdef',
                received: false,
                displayed: false,
                spoken: false
              }
            ]
          }
        ],
        total: 1
      })
    },
    currentUserId: 'user-001'
  })

  const { records } = await service.fetchNotificationRecords()

  assert.equal(records[0].deliveries[0].displayName, '设备 12345678')
  assert.equal(records[0].deliveries[0].displayMeta, 'ID 1234567890abcdef')
})

test('normalizeBindCode trims whitespace and uppercases input', () => {
  assert.equal(normalizeBindCode('  ab12cd  '), 'AB12CD')
})

test('normalizeBindCode does not treat tap event objects as codes', () => {
  assert.equal(normalizeBindCode({ type: 'tap' }), '')
})

test('getBindingErrorMessage explains expired or replaced binding codes', () => {
  assert.equal(
    getBindingErrorMessage({ message: 'binding code not found' }),
    '绑定码已失效，请重新扫码或刷新客户端绑定码'
  )
})

test('createBindingService fetches bind code device preview', async () => {
  const calls = []
  const service = createBindingService({
    request(options) {
      calls.push(options)
      return Promise.resolve({
        device_id: 'device-001',
        device_name: 'DESKTOP-ABC123',
        location_label: '',
        client_version: '0.1.0'
      })
    },
    currentUserId: 'user-001'
  })

  const result = await service.fetchBindCodeDevice({ code: ' ab12cd ' })

  assert.deepEqual(calls, [{ url: '/bindings/code/AB12CD/device' }])
  assert.deepEqual(result, {
    deviceId: 'device-001',
    deviceName: 'DESKTOP-ABC123',
    locationLabel: '',
    clientVersion: '0.1.0'
  })
})

test('createBindingService posts current user and editable device info', async () => {
  const calls = []
  const service = createBindingService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ user_id: 'user-001', device_id: 'device-001' })
    },
    currentUserId: 'user-001'
  })

  const result = await service.bindDevice({
    code: ' 123456 ',
    deviceName: '办公室提醒屏',
    locationLabel: '办公室'
  })

  assert.deepEqual(calls, [
    {
      url: '/bindings',
      method: 'POST',
      data: {
        user_id: 'user-001',
        code: '123456',
        device_name: '办公室提醒屏',
        location_label: '办公室'
      }
    }
  ])
  assert.deepEqual(result, { user_id: 'user-001', device_id: 'device-001' })
})

test('extractBindCodeFromScan supports raw bind code', () => {
  assert.equal(extractBindCodeFromScan('123456'), '123456')
})

test('extractBindCodeFromScan supports deep link content', () => {
  assert.equal(extractBindCodeFromScan('school-notify://bind?code=ab12cd'), 'AB12CD')
})

test('records keep createdAt when backend provides created_at', async () => {
  const service = createNotificationService({
    request() {
      return Promise.resolve({
        items: [
          {
            notification_id: 'notification-2',
            sender_user_id: 'user-001',
            title: '例会提醒',
            content: '请准时参加',
            level: 'important',
            target_count: 1,
            created_at: '2026-04-21T10:30:00Z',
            deliveries: []
          }
        ],
        total: 1
      })
    },
    currentUserId: 'user-001'
  })

  const { records } = await service.fetchNotificationRecords()

  assert.equal(records[0].createdAt, '2026-04-21T10:30:00Z')
})

test('getDurationSeconds maps preset durations', () => {
  assert.equal(getDurationSeconds({ durationIndex: 0, customDurationValue: '' }), 30)
  assert.equal(getDurationSeconds({ durationIndex: 1, customDurationValue: '' }), 60)
  assert.equal(getDurationSeconds({ durationIndex: 2, customDurationValue: '' }), 180)
  assert.equal(getDurationSeconds({ durationIndex: 3, customDurationValue: '' }), 300)
  assert.equal(getDurationSeconds({ durationIndex: 4, customDurationValue: '' }), 600)
})

test('getDurationSeconds uses custom duration in seconds', () => {
  assert.equal(getDurationSeconds({ durationIndex: 5, customDurationValue: '75' }), 75)
})

test('isCustomDurationSelected identifies custom option', () => {
  assert.equal(isCustomDurationSelected(5), true)
  assert.equal(isCustomDurationSelected(2), false)
})

test('hasAuthorizedProfile requires avatar and nickname', () => {
  assert.equal(hasAuthorizedProfile({ avatarUrl: 'https://example.com/a.png', nickName: 'Alice' }), true)
  assert.equal(hasAuthorizedProfile({ avatarUrl: '', nickName: 'Alice' }), false)
  assert.equal(hasAuthorizedProfile({ avatarUrl: 'https://example.com/a.png', nickName: '' }), false)
  assert.equal(hasAuthorizedProfile(null), false)
})

test('createUserProfile trims WeChat nickname and avatar values', () => {
  assert.deepEqual(
    createUserProfile({ avatarUrl: '  wxfile://avatar.png  ', nickName: ' 小张 ' }),
    { avatarUrl: 'wxfile://avatar.png', nickName: '小张' }
  )
})

test('createUserProfile keeps current nickname comparable for no-op confirmation', () => {
  const current = createUserProfile({ nickName: '小张' })
  const incoming = createUserProfile({ nickName: ' 小张 ' })

  assert.equal(current.nickName, incoming.nickName)
})

test('uploadAvatarToQiniu gets token, uploads file, and saves public avatar url', async () => {
  const calls = []
  const result = await uploadAvatarToQiniu({
    filePath: 'wxfile://avatar.png',
    nickname: '小张',
    request(options) {
      calls.push({ type: 'request', options })
      if (options.url === '/users/me/avatar/upload-token') {
        return Promise.resolve({
          upload_url: 'https://upload.qiniup.com',
          token: 'upload-token',
          key: 'avatars/user-001/20260516.png',
          public_url: 'https://img.schoolhelper.cn/avatars/user-001/20260516.png'
        })
      }
      return Promise.resolve({ avatar_url: options.data.avatar_url })
    },
    uploadFile(options) {
      calls.push({ type: 'upload', options })
      options.success({ statusCode: 200, data: '{"key":"avatars/user-001/20260516.png"}' })
    }
  })

  assert.equal(result, 'https://img.schoolhelper.cn/avatars/user-001/20260516.png')
  assert.equal(calls[0].type, 'request')
  assert.deepEqual(calls[0].options, { url: '/users/me/avatar/upload-token', method: 'POST' })
  assert.equal(calls[1].type, 'upload')
  assert.equal(calls[1].options.url, 'https://upload.qiniup.com')
  assert.equal(calls[1].options.filePath, 'wxfile://avatar.png')
  assert.equal(calls[1].options.name, 'file')
  assert.deepEqual(calls[1].options.formData, { token: 'upload-token', key: 'avatars/user-001/20260516.png' })
  assert.equal(calls[2].type, 'request')
  assert.deepEqual(calls[2].options, {
    url: '/users/me',
    method: 'PATCH',
    data: {
      nickname: '小张',
      avatar_url: 'https://img.schoolhelper.cn/avatars/user-001/20260516.png'
    }
  })
})

test('syncWechatProfile uploads avatar and returns trimmed profile data', async () => {
  const calls = []
  const profile = await syncWechatProfile({
    avatarFilePath: 'wxfile://avatar.png',
    nickName: ' 小张 ',
    request(options) {
      calls.push({ type: 'request', options })
      if (options.url === '/users/me/avatar/upload-token') {
        return Promise.resolve({
          upload_url: 'https://upload.qiniup.com',
          token: 'upload-token',
          key: 'avatars/user-001/20260522.png',
          public_url: 'https://img.schoolhelper.cn/avatars/user-001/20260522.png'
        })
      }
      return Promise.resolve({ ok: true })
    },
    uploadFile(options) {
      calls.push({ type: 'upload', options })
      options.success({ statusCode: 200, data: '{"key":"avatars/user-001/20260522.png"}' })
    }
  })

  assert.deepEqual(profile, {
    avatarUrl: 'https://img.schoolhelper.cn/avatars/user-001/20260522.png',
    nickName: '小张'
  })
  assert.equal(calls[0].options.url, '/users/me/avatar/upload-token')
  assert.equal(calls[1].type, 'upload')
  assert.deepEqual(calls[2].options, {
    url: '/users/me',
    method: 'PATCH',
    data: {
      nickname: '小张',
      avatar_url: 'https://img.schoolhelper.cn/avatars/user-001/20260522.png'
    }
  })
})

test('syncWechatProfile rejects when nickname-only save fails', async () => {
  await assert.rejects(
    syncWechatProfile({
      avatarUrl: 'https://img.schoolhelper.cn/avatars/user-001/20260522.png',
      nickName: '小张',
      request() {
        return Promise.reject(new Error('save failed'))
      }
    }),
    /save failed/
  )
})

test('profile page includes sync prompt action for incomplete profile', () => {
  const profileMarkup = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.wxml'), 'utf8')

  assert.equal(profileMarkup.includes('点头像同步微信头像，修改昵称后会自动保存。'), true)
  assert.match(profileMarkup, /class="profile-nick-input"/)
  assert.match(profileMarkup, /class="profile-nick-field"/)
  assert.match(profileMarkup, /bindblur="onNickNameConfirm"/)
  assert.match(profileMarkup, /bindconfirm="onNickNameConfirm"/)
  assert.doesNotMatch(profileMarkup, /onSyncWechatProfile/)
})

test('profile page nickname confirm ignores unchanged saved nickname', () => {
  const profileScript = fs.readFileSync(path.resolve(__dirname, '../pages/profile/index.js'), 'utf8')

  assert.match(profileScript, /profile\.nickName === currentNickName/)
})

test('send page keeps default title as 通知', () => {
  const sendScript = fs.readFileSync(path.resolve(__dirname, '../pages/send/index.js'), 'utf8')

  assert.match(sendScript, /title:\s*'通知'/)
})

test('miniapp user-facing copy avoids campus and education positioning', () => {
  const miniappRoot = path.resolve(__dirname, '..')
  const files = [
    'app.json',
    'pages/devices/index.wxml',
    'pages/send/index.wxml',
    'pages/bind/index.wxml',
    'pages/profile/index.wxml',
    'utils/login-gate.js'
  ]
  const blockedTerms = ['校园', '学校', '班级', '老师', '学生', '教室', '班委', '校务', '公告屏', '通知屏']

  const violations = []
  for (const file of files) {
    const content = fs.readFileSync(path.join(miniappRoot, file), 'utf8')
    for (const term of blockedTerms) {
      if (content.includes(term)) {
        violations.push(`${file}: ${term}`)
      }
    }
  }

  assert.deepEqual(violations, [])
})

test('hero titles leave enough line box room for Huawei font rendering', () => {
  const appStyle = fs.readFileSync(path.resolve(__dirname, '../app.wxss'), 'utf8')
  const sendStyle = fs.readFileSync(path.resolve(__dirname, '../pages/send/index.wxss'), 'utf8')
  const pageBodyRule = appStyle.match(/\.page-body\s*\{[\s\S]*?\n\}/)?.[0] || ''
  const heroTitleRule = appStyle.match(/\.hero-title\s*\{[\s\S]*?\n\}/)?.[0] || ''
  const sendTitleRule = sendStyle.match(/\.send-hero-title\s*\{[\s\S]*?\n\}/)?.[0] || ''
  const heroContentLayerRule = appStyle.match(/\.hero-simple-main,\n\.hero-overline,\n\.hero-title,\n\.hero-subtitle\s*\{[\s\S]*?\n\}/)?.[0] || ''

  assert.match(pageBodyRule, /padding:\s*24rpx\s+28rpx\s+calc\(132rpx \+ env\(safe-area-inset-bottom\)\);/)
  assert.match(heroTitleRule, /line-height:\s*1\.38;/)
  assert.match(heroTitleRule, /padding-bottom:\s*8rpx;/)
  assert.match(sendTitleRule, /line-height:\s*1\.38;/)
  assert.match(sendTitleRule, /padding-bottom:\s*8rpx;/)
  assert.match(heroContentLayerRule, /position:\s*relative;/)
  assert.match(heroContentLayerRule, /z-index:\s*2;/)
})

test('createLoggedInSession keeps stable default user id', () => {
  assert.deepEqual(
    createLoggedInSession({
      loginCode: 'wx-code-001',
      sessionToken: 'wechat-session:user-001',
      authProvider: 'wechat'
    }),
    {
      isLoggedIn: true,
      currentUserId: DEFAULT_USER_ID,
      loginCode: 'wx-code-001',
      sessionToken: 'wechat-session:user-001',
      authProvider: 'wechat',
      requiresManualLogin: false
    }
  )
})

test('logout session disables auto login until manual login', () => {
  const session = createLoggedOutSession()

  assert.equal(hasLoginSession(session), false)
  assert.equal(shouldAutoLogin(session), false)
})

test('hasLoginSession requires a session token', () => {
  assert.equal(hasLoginSession({ isLoggedIn: true, currentUserId: 'user-001', sessionToken: '' }), false)
})

test('missing session still allows initial auto login', () => {
  assert.equal(shouldAutoLogin(null), true)
})

test('getLoginRequiredMessage includes page title', () => {
  assert.equal(getLoginRequiredMessage('设备列表'), '无法查看当前设备列表页面，请登录')
})

test('createAuthService posts login code and returns backend session', async () => {
  const calls = []
  const service = createAuthService({
    request(options) {
      calls.push(options)
      return Promise.resolve({
        user_id: 'demo-user',
        session_token: 'mock-session-demo-user',
        auth_provider: 'wechat_mock',
        nickname: '张老师',
        avatar_url: 'https://img.schoolhelper.cn/avatars/demo-user/avatar.png'
      })
    }
  })

  const session = await service.login({ code: 'wx-code-001' })

  assert.deepEqual(calls, [
    {
      url: '/auth/login',
      method: 'POST',
      data: { code: 'wx-code-001' }
    }
  ])
  assert.deepEqual(session, {
    userId: 'demo-user',
    sessionToken: 'mock-session-demo-user',
    authProvider: 'wechat_mock',
    profile: {
      nickName: '张老师',
      avatarUrl: 'https://img.schoolhelper.cn/avatars/demo-user/avatar.png'
    }
  })
})

test('createAuthService calls logout endpoint', async () => {
  const calls = []
  const service = createAuthService({
    request(options) {
      calls.push(options)
      return Promise.resolve({})
    }
  })

  await service.logout()

  assert.deepEqual(calls, [
    {
      url: '/auth/logout',
      method: 'POST'
    }
  ])
})

test('createDeviceService deletes user binding for a device', async () => {
  const calls = []
  const service = createDeviceService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ user_id: 'user-001', device_id: 'device-001' })
    },
    currentUserId: 'user-001'
  })

  const result = await service.unbindDevice({ deviceId: 'device-001' })

  assert.deepEqual(calls, [
    {
      url: '/bindings/device-001?user_id=user-001',
      method: 'DELETE'
    }
  ])
  assert.deepEqual(result, { user_id: 'user-001', device_id: 'device-001' })
})

test('createDeviceService patches editable device info', async () => {
  const calls = []
  const service = createDeviceService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ device_id: 'device-001', device_name: '办公室提醒屏', location_label: '办公室' })
    },
    currentUserId: 'user-001'
  })

  const result = await service.updateDevice({
    deviceId: 'device-001',
    deviceName: ' 办公室提醒屏 ',
    locationLabel: ' 办公室 '
  })

  assert.deepEqual(calls, [
    {
      url: '/users/user-001/devices/device-001',
      method: 'PATCH',
      data: {
        device_name: '办公室提醒屏',
        location_label: '办公室'
      }
    }
  ])
  assert.deepEqual(result, { device_id: 'device-001', device_name: '办公室提醒屏', location_label: '办公室' })
})

test('buildRequestOptions adds bearer token when logged in', () => {
  const options = buildRequestOptions({
    apiBaseUrl: 'https://example.com/api',
    authSession: { sessionToken: 'wechat-session:openid-001' },
    url: '/devices',
    method: 'GET'
  })

  assert.deepEqual(options, {
    url: 'https://example.com/api/devices',
    method: 'GET',
    data: undefined,
    header: {
      Authorization: 'Bearer wechat-session:openid-001'
    }
  })
})

test('getErrorMessage formats FastAPI validation errors', () => {
  assert.equal(
    getErrorMessage({ detail: [{ msg: 'Field required' }, { msg: 'Invalid value' }] }),
    'Field required；Invalid value'
  )
})

test('createLoginGateModel builds page-specific login copy', () => {
  const model = createLoginGateModel('设备列表')

  assert.equal(model.eyebrow, '微信身份校验')
  assert.equal(model.title, '登录后查看设备列表')
  assert.equal(model.sceneLabel, '设备列表')
  assert.equal(model.highlights.length, 3)
  assert.equal(model.highlights[0], '同步你的设备归属关系')
})

test('createLoginGateModel falls back to generic highlights', () => {
  const model = createLoginGateModel('我的')

  assert.equal(model.sceneLabel, '我的')
  assert.equal(model.highlights[0], '恢复你的账号身份')
})
