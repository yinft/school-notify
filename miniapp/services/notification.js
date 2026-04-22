function createNotificationService({ request, currentUserId }) {
  return {
    sendNotification({ title, content, level, deviceIds, durationSeconds }) {
      return request({
        url: '/notifications',
        method: 'POST',
        data: {
          sender_user_id: currentUserId,
          title,
          content,
          level,
          device_ids: deviceIds,
          duration_seconds: durationSeconds
        }
      })
    },

    async fetchNotificationRecords() {
      const response = await request({
        url: `/notifications?sender_user_id=${encodeURIComponent(currentUserId)}`
      })

      return (response.items || []).map((item) => {
        const deliveries = (item.deliveries || []).map((delivery) => ({
          deviceId: delivery.device_id,
          received: delivery.received,
          displayed: delivery.displayed,
          spoken: delivery.spoken,
          statusText: delivery.spoken ? '已播报' : delivery.displayed ? '已展示' : delivery.received ? '已接收' : '待送达'
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
    }
  }
}

module.exports = {
  createNotificationService
}
