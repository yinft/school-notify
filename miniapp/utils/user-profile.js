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

function uploadFile({ uploadFileImpl, uploadUrl, filePath, token, key }) {
  return new Promise((resolve, reject) => {
    uploadFileImpl({
      url: uploadUrl,
      filePath,
      name: 'file',
      formData: { token, key },
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response)
          return
        }
        reject(new Error('avatar upload failed'))
      },
      fail(error) {
        reject(new Error(error.errMsg || 'avatar upload failed'))
      }
    })
  })
}

async function uploadAvatarToQiniu({ filePath, nickname, request: requestImpl = request, uploadFile: uploadFileImpl = wx.uploadFile }) {
  const uploadToken = await requestImpl({ url: '/users/me/avatar/upload-token', method: 'POST' })
  await uploadFile({
    uploadFileImpl,
    uploadUrl: uploadToken.upload_url,
    filePath,
    token: uploadToken.token,
    key: uploadToken.key
  })
  await requestImpl({
    url: '/users/me',
    method: 'PATCH',
    data: {
      nickname,
      avatar_url: uploadToken.public_url
    }
  })
  return uploadToken.public_url
}

module.exports = {
  USER_PROFILE_STORAGE_KEY,
  createUserProfile,
  hasAuthorizedProfile,
  uploadAvatarToQiniu,
  syncProfileToServer
}
