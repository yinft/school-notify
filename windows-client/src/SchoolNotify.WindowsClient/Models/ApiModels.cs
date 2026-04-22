namespace SchoolNotify.WindowsClient.Models;

public sealed record DeviceRegistrationRequest(string DeviceId, string DeviceName, string ClientVersion);

public sealed record DeviceResponse(string DeviceId, string DeviceName, string ClientVersion, string Status, System.DateTimeOffset LastSeenAt, string DeviceToken = "");

public sealed record BindingCodeResponse(string DeviceId, string Code, int ExpiresInSeconds);
