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

    async fetchNotificationRecords({ limit, offset } = {}) {
      let url = `/notifications?sender_user_id=${encodeURIComponent(currentUserId)}`
      if (limit !== undefined) url += `&limit=${limit}`
      if (offset !== undefined) url += `&offset=${offset}`

      const response = await request({ url })

      const records = (response.items || []).map((item) => {
        const deliveries = (item.deliveries || []).map((delivery) => ({
          deviceId: delivery.device_id,
          received: delivery.received,
          displayed: delivery.displayed,
          spoken: delivery.spoken,
          failed: Boolean(delivery.failed),
          errorMessage: delivery.error_message || '',
          statusText: delivery.failed ? '投递失败' : delivery.spoken ? '已播报' : delivery.displayed ? '已展示' : delivery.received ? '已接收' : '待送达'
        }))
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

module.exports = {
  createNotificationService
}
