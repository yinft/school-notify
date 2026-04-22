const PRESET_DURATION_SECONDS = [30, 60, 180, 300, 600]
const CUSTOM_DURATION_INDEX = 5

function isCustomDurationSelected(durationIndex) {
  return Number(durationIndex) === CUSTOM_DURATION_INDEX
}

function getDurationSeconds({ durationIndex, customDurationValue }) {
  if (!isCustomDurationSelected(durationIndex)) {
    return PRESET_DURATION_SECONDS[Number(durationIndex)]
  }

  return Number(customDurationValue)
}

module.exports = {
  PRESET_DURATION_SECONDS,
  CUSTOM_DURATION_INDEX,
  isCustomDurationSelected,
  getDurationSeconds
}
