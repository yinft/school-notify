namespace SchoolNotify.WindowsClient.Models;

public sealed record ClientSettings(bool AutoStartEnabled = true)
{
    public static ClientSettings Default { get; } = new(AutoStartEnabled: true);
}
