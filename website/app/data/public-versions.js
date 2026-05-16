export async function loadPublicVersionItems(fetcher, backendBaseUrl) {
  const normalizedBaseUrl = backendBaseUrl?.trim()

  if (!normalizedBaseUrl) {
    return []
  }

  try {
    const response = await fetcher(`${normalizedBaseUrl}/api/public/versions?platform=windows`)

    return Array.isArray(response?.items) ? response.items : []
  } catch {
    return []
  }
}
