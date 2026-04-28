const test = require('node:test')
const assert = require('node:assert/strict')

const { createDeviceService, formatLastSeenText } = require('../services/device')
const { createBindingService, extractBindCodeFromScan, normalizeBindCode } = require('../services/binding')
const { createNotificationService } = require('../services/notification')
const { createAuthService } = require('../services/auth')
const { getDurationSeconds, isCustomDurationSelected } = require('../pages/send/duration')
const { createLoginGateModel } = require('../utils/login-gate')
const { buildRequestOptions, getErrorMessage } = require('../utils/request')
const { createUserProfile, hasAuthorizedProfile } = require('../utils/user-profile')
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

test('formatLastSeenText formats iso timestamps', () => {
  assert.equal(formatLastSeenText('2026-04-21T08:00:00Z'), '最后在线：2026-04-21 08:00')
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
            location_label: '高一3班教室',
            client_version: '0.1.0',
            status: 'online',
            last_seen_at: '2026-04-21T08:00:00Z'
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
      locationLabel: '高一3班教室',
      clientVersion: '0.1.0',
      status: 'online',
      lastSeenAt: '2026-04-21T08:00:00Z',
      lastSeenText: '最后在线：2026-04-21 08:00',
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
    title: '紧急通知',
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
        title: '紧急通知',
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
            title: '紧急通知',
            content: '请立即集合',
            level: 'urgent',
            target_count: 1,
            deliveries: [
              {
                device_id: 'device-001',
                device_name: '三年级一班通知屏',
                location_label: '三年级一班教室',
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
      title: '紧急通知',
      content: '请立即集合',
      level: 'urgent',
      targetCount: 1,
      deliverySummary: '1 台设备，1 台已展示',
      deliveries: [
        {
          deviceId: 'device-001',
          deviceName: '三年级一班通知屏',
          locationLabel: '三年级一班教室',
          displayName: '三年级一班通知屏',
          displayMeta: '三年级一班教室',
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
    deviceName: '三年级一班通知屏',
    locationLabel: '三年级一班教室'
  })

  assert.deepEqual(calls, [
    {
      url: '/bindings',
      method: 'POST',
      data: {
        user_id: 'user-001',
        code: '123456',
        device_name: '三年级一班通知屏',
        location_label: '三年级一班教室'
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
    createUserProfile({ avatarUrl: '  wxfile://avatar.png  ', nickName: ' 张老师 ' }),
    { avatarUrl: 'wxfile://avatar.png', nickName: '张老师' }
  )
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
        auth_provider: 'wechat_mock'
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
    authProvider: 'wechat_mock'
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
      return Promise.resolve({ device_id: 'device-001', device_name: '三年级一班通知屏', location_label: '三年级一班教室' })
    },
    currentUserId: 'user-001'
  })

  const result = await service.updateDevice({
    deviceId: 'device-001',
    deviceName: ' 三年级一班通知屏 ',
    locationLabel: ' 三年级一班教室 '
  })

  assert.deepEqual(calls, [
    {
      url: '/users/user-001/devices/device-001',
      method: 'PATCH',
      data: {
        device_name: '三年级一班通知屏',
        location_label: '三年级一班教室'
      }
    }
  ])
  assert.deepEqual(result, { device_id: 'device-001', device_name: '三年级一班通知屏', location_label: '三年级一班教室' })
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
