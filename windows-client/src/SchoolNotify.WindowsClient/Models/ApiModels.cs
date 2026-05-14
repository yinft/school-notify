using System.Text.Json.Serialization;

namespace SchoolNotify.WindowsClient.Models;

public sealed record DeviceRegistrationRequest(
    [property: JsonPropertyName("device_id")] string DeviceId,
    [property: JsonPropertyName("device_name")] string DeviceName,
    [property: JsonPropertyName("client_version")] string ClientVersion);

public sealed record DeviceResponse(
    [property: JsonPropertyName("device_id")] string DeviceId,
    [property: JsonPropertyName("device_name")] string DeviceName,
    [property: JsonPropertyName("location_label")] string LocationLabel,
    [property: JsonPropertyName("client_version")] string ClientVersion,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("last_seen_at")] System.DateTimeOffset LastSeenAt,
    [property: JsonPropertyName("device_token")] string DeviceToken = "",
    [property: JsonPropertyName("update")] DeviceUpdateInfo? Update = null);

public sealed record DeviceUpdateInfo(
    [property: JsonPropertyName("available")] bool Available,
    [property: JsonPropertyName("current_version")] string CurrentVersion,
    [property: JsonPropertyName("latest_version")] string? LatestVersion = null,
    [property: JsonPropertyName("download_url")] string? DownloadUrl = null,
    [property: JsonPropertyName("file_size")] int? FileSize = null);

public sealed record BindingCodeResponse(
    [property: JsonPropertyName("device_id")] string DeviceId,
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("expires_in_seconds")] int ExpiresInSeconds);
