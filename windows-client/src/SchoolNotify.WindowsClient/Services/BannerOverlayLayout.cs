namespace SchoolNotify.WindowsClient.Services;

public sealed record BannerOverlayPlacement(double Left, double Top, double Width, double Height, bool ShouldScroll);

public static class BannerOverlayLayout
{
    public static BannerOverlayPlacement Build(string displayMode, double screenWidth, double screenHeight, double topBannerHeight = 100)
    {
        if (displayMode == Models.BannerDisplayModes.FullScreen)
        {
            return new BannerOverlayPlacement(0, 0, screenWidth, screenHeight, ShouldScroll: false);
        }

        return new BannerOverlayPlacement(0, 0, screenWidth, topBannerHeight, ShouldScroll: true);
    }
}
