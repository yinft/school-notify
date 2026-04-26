function normalizeBindCode(code) {
  return String(code || '').trim().toUpperCase()
}

function extractBindCodeFromScan(scanResult) {
  const normalized = normalizeBindCode(scanResult)
  if (!normalized) {
    return ''
  }

  if (/^[A-Z0-9]{6,12}$/.test(normalized)) {
    return normalized
  }

  const match = String(scanResult).match(/[?&]code=([^&#]+)/i)
  if (!match) {
    return ''
  }

  return normalizeBindCode(decodeURIComponent(match[1]))
}

function createBindingService({ request, currentUserId }) {
  return {
    async fetchBindCodeDevice({ code }) {
      const response = await request({ url: `/bindings/code/${encodeURIComponent(normalizeBindCode(code))}/device` })
      return {
        deviceId: response.device_id,
        deviceName: response.device_name,
        locationLabel: response.location_label || '',
        clientVersion: response.client_version
      }
    },

    bindDevice({ code, deviceName = '', locationLabel = '' }) {
      return request({
        url: '/bindings',
        method: 'POST',
        data: {
          user_id: currentUserId,
          code: normalizeBindCode(code),
          device_name: String(deviceName || '').trim(),
          location_label: String(locationLabel || '').trim()
        }
      })
    }
  }
}

module.exports = {
  createBindingService,
  extractBindCodeFromScan,
  normalizeBindCode
}
