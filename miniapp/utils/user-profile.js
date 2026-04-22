const USER_PROFILE_STORAGE_KEY = 'userProfile'

const { request } = require('./request')

function hasAuthorizedProfile(profile) {
  return Boolean(profile && profile.avatarUrl && profile.nickName)
}

async function syncProfileToServer({ nickname, avatarUrl }) {
  const payload = {}
  if (nickname) payload.nickname = nickname
  if (avatarUrl) payload.avatar_url = avatarUrl
  try {
    const result = await request({ url: '/api/users/me', method: 'PATCH', data: payload })
    return result
  } catch {
    return null
  }
}

module.exports = {
  USER_PROFILE_STORAGE_KEY,
  hasAuthorizedProfile,
  syncProfileToServer
}
