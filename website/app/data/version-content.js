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

  const [latest, ...rest] = items
  const releases = [latest, ...rest].map((item) => ({
    version: `v${item.version}`,
    date: toDateLabel(item.published_at),
    summary: item.release_notes || 'Windows 桌面端个人试用版，用于固定电脑上的轻量提醒。',
    items: [item.release_notes || '适合个人固定电脑试用。']
  }))

  return {
    download: {
      ...siteContent.download,
      version: latest.version,
      updatedAt: toDateLabel(latest.published_at),
      href: latest.download_url
    },
    releases
  }
}
