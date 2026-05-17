import { siteContent } from './site-content.js'

function toDateLabel(value) {
  if (!value) {
    return siteContent.download.updatedAt
  }

  return value.slice(0, 10)
}

export function buildVersionContent(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return {
      download: siteContent.download,
      releases: siteContent.releases
    }
  }

  const downloadTarget = items.find((item) => item?.is_recommended) || items[0]
  const releases = items.slice(0, 3).map((item) => ({
    version: `v${item.version}`,
    date: toDateLabel(item.published_at),
    summary: item.release_notes || 'Windows 桌面端个人试用版，用于固定电脑上的轻量提醒。',
    items: [item.release_notes || '适合个人固定电脑试用。']
  }))

  return {
    download: {
      ...siteContent.download,
      version: downloadTarget.version,
      updatedAt: toDateLabel(downloadTarget.published_at),
      href: downloadTarget.download_url
    },
    releases
  }
}
