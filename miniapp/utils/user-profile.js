const USER_PROFILE_STORAGE_KEY = 'userProfile'

const { request } = require('./request')

function hasAuthorizedProfile(profile) {
  return Boolean(profile && profile.avatarUrl && profile.nickName)
}

function createUserProfile({ avatarUrl = '', nickName = '' } = {}) {
  return {
    avatarUrl: String(avatarUrl || '').trim(),
    nickName: String(nickName || '').trim()
  }
}

async function syncProfileToServer({ nickname, avatarUrl }) {
  const payload = {}
  if (nickname) payload.nickname = nickname
  if (avatarUrl) payload.avatar_url = avatarUrl
  try {
    const result = await request({ url: '/users/me', method: 'PATCH', data: payload })
    return result
  } catch {
    return null
  }
}

module.exports = {
  USER_PROFILE_STORAGE_KEY,
  createUserProfile,
  hasAuthorizedProfile,
  syncProfileToServer
}
