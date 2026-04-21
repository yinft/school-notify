namespace SchoolNotify.WindowsClient.Services;

public static class SpeechAnnouncementFormatter
{
    public static string Format(string title, string content, string level)
    {
        var normalizedTitle = string.IsNullOrWhiteSpace(title) ? "通知" : title.Trim();
        var normalizedContent = string.IsNullOrWhiteSpace(content) ? string.Empty : content.Trim();
        var prefix = level == "urgent" ? "紧急通知。" : string.Empty;

        return string.IsNullOrWhiteSpace(normalizedContent)
            ? $"{prefix}{normalizedTitle}。"
            : $"{prefix}{normalizedTitle}。{normalizedContent}。";
    }
}
