const USER_PROFILE_STORAGE_KEY = 'userProfile'

function hasAuthorizedProfile(profile) {
  return Boolean(profile && profile.avatarUrl && profile.nickName)
}

module.exports = {
  USER_PROFILE_STORAGE_KEY,
  hasAuthorizedProfile
}
