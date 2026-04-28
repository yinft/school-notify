namespace SchoolNotify.WindowsClient.Services;

public readonly record struct BannerScrollMetrics(double ViewportWidth, double ContentWidth)
{
    public static BannerScrollMetrics? Resolve(double viewportWidth, double actualTextWidth, double desiredTextWidth)
    {
        if (viewportWidth <= 1d)
        {
            return null;
        }

        var contentWidth = actualTextWidth > 1d ? actualTextWidth : desiredTextWidth;
        if (contentWidth <= 1d)
        {
            return null;
        }

        return new BannerScrollMetrics(viewportWidth, contentWidth);
    }
}
