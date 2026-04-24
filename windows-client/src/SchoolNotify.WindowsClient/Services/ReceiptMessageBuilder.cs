using System.Text.Json;
using System.Text.Json.Serialization;

namespace SchoolNotify.WindowsClient.Services;

public static class ReceiptMessageBuilder
{
    public static string Build(string eventName, string notificationId)
    {
        return JsonSerializer.Serialize(new ReceiptMessage(eventName, notificationId));
    }

    private sealed record ReceiptMessage(
        [property: JsonPropertyName("event")] string Event,
        [property: JsonPropertyName("notification_id")] string NotificationId);
}
