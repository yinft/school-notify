function createNotificationService({ request, currentUserId }) {
  return {
    sendNotification({ title, content, level, deviceIds, durationSeconds, ttsEnabled, ttsRepeatCount }) {
      return request({
        url: '/notifications',
        method: 'POST',
        data: {
          sender_user_id: currentUserId,
          title,
          content,
          level,
          device_ids: deviceIds,
          duration_seconds: durationSeconds,
          tts_enabled: ttsEnabled,
          tts_repeat_count: ttsRepeatCount
        }
      })
    },

    async fetchNotificationRecords({ limit, offset, startAt, endAt } = {}) {
      let url = `/notifications?sender_user_id=${encodeURIComponent(currentUserId)}`
      if (limit !== undefined) url += `&limit=${limit}`
      if (offset !== undefined) url += `&offset=${offset}`
      if (startAt) url += `&start_at=${encodeURIComponent(startAt)}`
      if (endAt) url += `&end_at=${encodeURIComponent(endAt)}`

      const response = await request({ url })

      const records = (response.items || []).map((item) => {
        const deliveries = (item.deliveries || []).map(mapDelivery)
        const displayedCount = deliveries.filter((delivery) => delivery.displayed).length

        return {
          id: item.notification_id,
          title: item.title,
          content: item.content,
          level: item.level,
          ...(item.created_at ? { createdAt: item.created_at } : {}),
          targetCount: item.target_count,
          deliverySummary: `${item.target_count} 台设备，${displayedCount} 台已展示`,
          deliveries
        }
      })

      return { records, total: response.total || 0 }
    }
  }
}

function mapDelivery(delivery) {
  const deviceId = delivery.device_id || ''
  const deviceName = delivery.device_name || ''
  const locationLabel = delivery.location_label || ''

  return {
    deviceId,
    deviceName,
    locationLabel,
    displayName: deviceName || `设备 ${deviceId.slice(0, 8)}`,
    displayMeta: locationLabel || (deviceId ? `ID ${deviceId}` : ''),
    received: delivery.received,
    displayed: delivery.displayed,
    spoken: delivery.spoken,
    failed: Boolean(delivery.failed),
    errorMessage: delivery.error_message || '',
    statusText: delivery.failed ? '投递失败' : delivery.spoken ? '已播报' : delivery.displayed ? '已展示' : delivery.received ? '已接收' : '待送达'
  }
}

module.exports = {
  createNotificationService
}
