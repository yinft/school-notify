using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class BannerDisplayModeTests
{
    [Fact]
    public void BannerSettings_DefaultUsesFullScreenMode()
    {
        Assert.Equal(BannerDisplayModes.FullScreen, BannerSettings.Default.DisplayMode);
    }

    [Fact]
    public void BannerOverlayLayout_BuildsTopBannerBounds()
    {
        var layout = BannerOverlayLayout.Build(BannerDisplayModes.TopBanner, screenWidth: 1920, screenHeight: 1080, topBannerHeight: 100);

        Assert.Equal(0, layout.Left);
        Assert.Equal(0, layout.Top);
        Assert.Equal(1920, layout.Width);
        Assert.Equal(100, layout.Height);
        Assert.True(layout.ShouldScroll);
    }

    [Fact]
    public void BannerOverlayLayout_BuildsTopBannerBoundsWithCustomHeight()
    {
        var layout = BannerOverlayLayout.Build(BannerDisplayModes.TopBanner, screenWidth: 1920, screenHeight: 1080, topBannerHeight: 160);

        Assert.Equal(160, layout.Height);
    }

    [Fact]
    public void BannerOverlayLayout_BuildsFullscreenBounds()
    {
        var layout = BannerOverlayLayout.Build(BannerDisplayModes.FullScreen, screenWidth: 1920, screenHeight: 1080, topBannerHeight: 100);

        Assert.Equal(0, layout.Left);
        Assert.Equal(0, layout.Top);
        Assert.Equal(1920, layout.Width);
        Assert.Equal(1080, layout.Height);
        Assert.False(layout.ShouldScroll);
    }
}
