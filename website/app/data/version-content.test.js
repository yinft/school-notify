import test from 'node:test'
import assert from 'node:assert/strict'

import { buildVersionContent } from './version-content.js'

test('prefers recommended version for download and limits releases to latest three', () => {
  const content = buildVersionContent([
    {
      version: '1.4.0',
      release_notes: 'latest published',
      published_at: '2026-05-17T10:00:00',
      download_url: 'https://example.com/1.4.0.zip',
      is_recommended: false
    },
    {
      version: '1.3.0',
      release_notes: 'recommended stable',
      published_at: '2026-05-16T10:00:00',
      download_url: 'https://example.com/1.3.0.zip',
      is_recommended: true
    },
    {
      version: '1.2.0',
      release_notes: 'older release',
      published_at: '2026-05-15T10:00:00',
      download_url: 'https://example.com/1.2.0.zip',
      is_recommended: false
    },
    {
      version: '1.1.0',
      release_notes: 'oldest release',
      published_at: '2026-05-14T10:00:00',
      download_url: 'https://example.com/1.1.0.zip',
      is_recommended: false
    }
  ])

  assert.equal(content.download.version, '1.3.0')
  assert.equal(content.download.href, 'https://example.com/1.3.0.zip')
  assert.deepEqual(
    content.releases.map((item) => item.version),
    ['v1.4.0', 'v1.3.0', 'v1.2.0']
  )
})

test('falls back to latest published version when no recommendation exists', () => {
  const content = buildVersionContent([
    {
      version: '1.4.0',
      release_notes: 'latest published',
      published_at: '2026-05-17T10:00:00',
      download_url: 'https://example.com/1.4.0.zip',
      is_recommended: false
    },
    {
      version: '1.3.0',
      release_notes: 'older release',
      published_at: '2026-05-16T10:00:00',
      download_url: 'https://example.com/1.3.0.zip',
      is_recommended: false
    }
  ])

  assert.equal(content.download.version, '1.4.0')
  assert.equal(content.download.href, 'https://example.com/1.4.0.zip')
})
