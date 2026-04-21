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
    bindDevice({ code }) {
      return request({
        url: '/bindings',
        method: 'POST',
        data: {
          user_id: currentUserId,
          code: normalizeBindCode(code)
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
