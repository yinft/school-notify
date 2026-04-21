namespace SchoolNotify.WindowsClient.Models;

public sealed record DeviceNotificationPayload(string NotificationId, string Title, string Content, string Level);

public sealed record DeviceNotificationMessage(string Event, string DeviceId, DeviceNotificationPayload Payload);
