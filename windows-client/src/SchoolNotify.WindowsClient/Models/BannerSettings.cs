namespace SchoolNotify.WindowsClient.Models;

public sealed record BannerSettings(
    double ScrollSpeed,
    double FontSize,
    string NormalColorName,
    string ImportantColorName,
    string UrgentColorName,
    int DisplayDurationSeconds,
    string DisplayMode = BannerDisplayModes.TopBanner)
{
    public static BannerSettings Default { get; } = new(160, 24, "SteelBlue", "Orange", "Red", 10, BannerDisplayModes.TopBanner);
}

public static class BannerDisplayModes
{
    public const string TopBanner = "TopBanner";
    public const string FullScreen = "FullScreen";
}
