namespace SchoolNotify.WindowsClient.Models;

public sealed record BannerSettings(
    double ScrollSpeed,
    double FontSize,
    string NormalColorName,
    string ImportantColorName,
    string UrgentColorName,
    int DisplayDurationSeconds,
    double BannerHeight = 100,
    string DisplayMode = BannerDisplayModes.FullScreen)
{
    public static BannerSettings Default { get; } = new(160, 24, "SteelBlue", "Orange", "Red", 10, 100, BannerDisplayModes.FullScreen);
}

public static class BannerDisplayModes
{
    public const string TopBanner = "TopBanner";
    public const string FullScreen = "FullScreen";
}
