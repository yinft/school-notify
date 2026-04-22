const test = require('node:test')
const assert = require('node:assert/strict')

const { createDeviceService, formatLastSeenText } = require('../services/device')
const { createBindingService, extractBindCodeFromScan, normalizeBindCode } = require('../services/binding')
const { createNotificationService } = require('../services/notification')
const { getDurationSeconds, isCustomDurationSelected } = require('../pages/send/duration')
const { hasAuthorizedProfile } = require('../utils/user-profile')

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
    durationSeconds: 30
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
        duration_seconds: 30
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
                received: true,
                displayed: true,
                spoken: false
              }
            ]
          }
        ]
      })
    },
    currentUserId: 'user-001'
  })

  const records = await service.fetchNotificationRecords()

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
          received: true,
          displayed: true,
          spoken: false,
          statusText: '已展示'
        }
      ]
    }
  ])
})

test('normalizeBindCode trims whitespace and uppercases input', () => {
  assert.equal(normalizeBindCode('  ab12cd  '), 'AB12CD')
})

test('createBindingService posts current user and normalized code', async () => {
  const calls = []
  const service = createBindingService({
    request(options) {
      calls.push(options)
      return Promise.resolve({ user_id: 'user-001', device_id: 'device-001' })
    },
    currentUserId: 'user-001'
  })

  const result = await service.bindDevice({ code: ' 123456 ' })

  assert.deepEqual(calls, [
    {
      url: '/bindings',
      method: 'POST',
      data: {
        user_id: 'user-001',
        code: '123456'
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
        ]
      })
    },
    currentUserId: 'user-001'
  })

  const [record] = await service.fetchNotificationRecords()

  assert.equal(record.createdAt, '2026-04-21T10:30:00Z')
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
