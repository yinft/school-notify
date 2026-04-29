function toggleSelectedDevice(selectedDeviceIds, deviceId) {
  if (!deviceId) {
    return selectedDeviceIds.slice()
  }

  if (selectedDeviceIds.includes(deviceId)) {
    return selectedDeviceIds.filter((id) => id !== deviceId)
  }

  return selectedDeviceIds.concat(deviceId)
}

module.exports = {
  toggleSelectedDevice
}
