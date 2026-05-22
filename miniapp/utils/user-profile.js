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

async function syncProfileToServer({ nickname, avatarUrl, request: requestImpl = request }) {
  const payload = {}
  if (nickname) payload.nickname = nickname
  if (avatarUrl) payload.avatar_url = avatarUrl
  return requestImpl({ url: '/users/me', method: 'PATCH', data: payload })
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

async function uploadAvatarToQiniu({ filePath, nickname, request: requestImpl = request, uploadFile: uploadFileImpl }) {
  const resolvedUploadFile = uploadFileImpl || wx.uploadFile
  const uploadToken = await requestImpl({ url: '/users/me/avatar/upload-token', method: 'POST' })
  await uploadFile({
    uploadFileImpl: resolvedUploadFile,
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

async function syncWechatProfile({
  avatarFilePath = '',
  avatarUrl = '',
  nickName = '',
  request: requestImpl = request,
  uploadFile: uploadFileImpl
}) {
  const profile = createUserProfile({ avatarUrl, nickName })
  const nextAvatarUrl = avatarFilePath
    ? await uploadAvatarToQiniu({
      filePath: avatarFilePath,
      nickname: profile.nickName,
      request: requestImpl,
      uploadFile: uploadFileImpl
    })
    : profile.avatarUrl

  if (!avatarFilePath) {
    await syncProfileToServer({ nickname: profile.nickName, avatarUrl: nextAvatarUrl, request: requestImpl })
  }

  return createUserProfile({ avatarUrl: nextAvatarUrl, nickName: profile.nickName })
}

module.exports = {
  USER_PROFILE_STORAGE_KEY,
  createUserProfile,
  hasAuthorizedProfile,
  uploadAvatarToQiniu,
  syncProfileToServer,
  syncWechatProfile
}
