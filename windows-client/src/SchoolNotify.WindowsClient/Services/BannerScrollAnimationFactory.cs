using System.Windows.Media.Animation;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public static class BannerScrollAnimationFactory
{
    public static DoubleAnimation Build(double viewportWidth, double contentWidth, BannerSettings settings)
    {
        var safeViewportWidth = Math.Max(1d, viewportWidth);
        var safeContentWidth = Math.Max(1d, contentWidth);
        var safePixelsPerSecond = Math.Max(1d, settings.ScrollSpeed);
        var duration = TimeSpan.FromSeconds((safeViewportWidth + safeContentWidth) / safePixelsPerSecond);

        return new DoubleAnimation
        {
            From = safeViewportWidth,
            To = -safeContentWidth,
            Duration = new System.Windows.Duration(duration),
            RepeatBehavior = RepeatBehavior.Forever,
        };
    }
}
