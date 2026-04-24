function formatLastSeenText(lastSeenAt) {
  if (!lastSeenAt) {
    return '暂无在线记录'
  }

  const normalized = String(lastSeenAt).replace('T', ' ').replace('Z', '')
  return `最后在线：${normalized.slice(0, 16)}`
}

function mapDevice(device) {
  return {
    id: device.device_id,
    name: device.device_name,
    clientVersion: device.client_version,
    status: device.status,
    lastSeenAt: device.last_seen_at,
    lastSeenText: formatLastSeenText(device.last_seen_at),
    statusText: device.status === 'online' ? '在线' : '离线'
  }
}

function createDeviceService({ request, currentUserId }) {
  return {
    async fetchUserDevices() {
      const response = await request({ url: `/users/${currentUserId}/devices` })
      return (response.items || []).map(mapDevice)
    },

    unbindDevice({ deviceId }) {
      return request({
        url: `/bindings/${encodeURIComponent(deviceId)}?user_id=${encodeURIComponent(currentUserId)}`,
        method: 'DELETE'
      })
    }
  }
}

module.exports = {
  createDeviceService,
  formatLastSeenText
}
