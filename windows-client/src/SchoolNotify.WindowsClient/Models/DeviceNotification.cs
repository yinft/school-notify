using System.Text.Json.Serialization;

namespace SchoolNotify.WindowsClient.Models;

public sealed record DeviceNotificationPayload(
    [property: JsonPropertyName("notification_id")] string NotificationId,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("level")] string Level,
    [property: JsonPropertyName("duration_seconds")] int? DurationSeconds = null,
    [property: JsonPropertyName("tts_enabled")] bool TtsEnabled = true,
    [property: JsonPropertyName("tts_repeat_count")] int? TtsRepeatCount = null);

public sealed record DeviceNotificationMessage(
    [property: JsonPropertyName("event")] string Event,
    [property: JsonPropertyName("device_id")] string DeviceId,
    [property: JsonPropertyName("payload")] DeviceNotificationPayload Payload);
