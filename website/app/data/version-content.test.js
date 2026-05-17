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

test('does not duplicate version prefix when backend version already starts with v', () => {
  const content = buildVersionContent([
    {
      version: 'v1',
      release_notes: 'single-line notes',
      published_at: '2026-05-17T10:00:00',
      download_url: 'https://example.com/v1.zip',
      is_recommended: true
    }
  ])

  assert.equal(content.download.version, 'v1')
  assert.deepEqual(content.releases.map((item) => item.version), ['v1'])
})

test('maps backend release notes to plain detail text', () => {
  const content = buildVersionContent([
    {
      version: '1.4.0',
      release_notes: 'fixed desktop banner timing',
      published_at: '2026-05-17T10:00:00',
      download_url: 'https://example.com/1.4.0.zip',
      is_recommended: false
    }
  ])

  assert.equal(content.releases[0].detail, 'fixed desktop banner timing')
  assert.equal('items' in content.releases[0], false)
})
