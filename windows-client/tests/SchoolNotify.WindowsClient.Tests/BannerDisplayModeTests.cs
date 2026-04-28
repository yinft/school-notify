using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class BannerDisplayModeTests
{
    [Fact]
    public void BannerSettings_DefaultUsesTopBannerMode()
    {
        Assert.Equal(BannerDisplayModes.TopBanner, BannerSettings.Default.DisplayMode);
    }

    [Fact]
    public void BannerOverlayLayout_BuildsTopBannerBounds()
    {
        var layout = BannerOverlayLayout.Build(BannerDisplayModes.TopBanner, screenWidth: 1920, screenHeight: 1080);

        Assert.Equal(0, layout.Left);
        Assert.Equal(0, layout.Top);
        Assert.Equal(1920, layout.Width);
        Assert.Equal(64, layout.Height);
        Assert.True(layout.ShouldScroll);
    }

    [Fact]
    public void BannerOverlayLayout_BuildsFullscreenBounds()
    {
        var layout = BannerOverlayLayout.Build(BannerDisplayModes.FullScreen, screenWidth: 1920, screenHeight: 1080);

        Assert.Equal(0, layout.Left);
        Assert.Equal(0, layout.Top);
        Assert.Equal(1920, layout.Width);
        Assert.Equal(1080, layout.Height);
        Assert.False(layout.ShouldScroll);
    }
}
