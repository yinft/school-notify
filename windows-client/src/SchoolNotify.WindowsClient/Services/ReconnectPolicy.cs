namespace SchoolNotify.WindowsClient.Services;

public static class ReconnectPolicy
{
    public static TimeSpan GetDelay(int attempt)
    {
        var normalizedAttempt = Math.Max(1, attempt);
        var seconds = 2;
        for (var index = 1; index < normalizedAttempt; index += 1)
        {
            seconds = Math.Min(30, seconds * 2);
        }

        return TimeSpan.FromSeconds(seconds);
    }
}
