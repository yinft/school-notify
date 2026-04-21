namespace SchoolNotify.WindowsClient.Services;

public static class ReceiptMessageBuilder
{
    public static string Build(string eventName, string notificationId)
    {
        return $"{{\"event\":\"{eventName}\",\"notification_id\":\"{notificationId}\"}}";
    }
}
