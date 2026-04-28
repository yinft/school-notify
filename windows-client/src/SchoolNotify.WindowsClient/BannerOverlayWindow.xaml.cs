using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Animation;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;

namespace SchoolNotify.WindowsClient;

public partial class BannerOverlayWindow : Window
{
    public BannerOverlayWindow()
    {
        InitializeComponent();
    }

    public void ShowNotification(string text, string colorName, BannerSettings settings)
    {
        ApplyLayout(settings.DisplayMode);
        MarqueeTextBlock.Text = text;
        MarqueeTextBlock.FontSize = settings.FontSize;
        BannerBorder.Background = ResolveBrush(colorName);
        Visibility = Visibility.Visible;
        UpdateLayout();
        if (settings.DisplayMode == BannerDisplayModes.FullScreen)
        {
            StopScroll();
            return;
        }

        StartScroll(settings);
    }

    public void HideNotification()
    {
        StopScroll();
        Visibility = Visibility.Collapsed;
    }

    private void CloseButtonClicked(object sender, RoutedEventArgs e)
    {
        HideNotification();
    }

    private void StartScroll(BannerSettings settings)
    {
        if (Visibility != Visibility.Visible)
        {
            return;
        }

        MarqueeTextBlock.Measure(new System.Windows.Size(double.PositiveInfinity, BannerViewport.ActualHeight));
        var metrics = BannerScrollMetrics.Resolve(
            BannerViewport.ActualWidth,
            MarqueeTextBlock.ActualWidth,
            MarqueeTextBlock.DesiredSize.Width);
        if (metrics is null)
        {
            Dispatcher.BeginInvoke(() => StartScroll(settings), System.Windows.Threading.DispatcherPriority.Loaded);
            return;
        }

        var animation = BannerScrollAnimationFactory.Build(
            metrics.Value.ViewportWidth,
            metrics.Value.ContentWidth,
            settings);

        MarqueeTransform.BeginAnimation(TranslateTransform.XProperty, animation, HandoffBehavior.SnapshotAndReplace);
    }

    private void ApplyLayout(string displayMode)
    {
        var layout = Services.BannerOverlayLayout.Build(
            displayMode,
            SystemParameters.PrimaryScreenWidth,
            SystemParameters.PrimaryScreenHeight);
        Left = layout.Left;
        Top = layout.Top;
        Width = layout.Width;
        Height = layout.Height;

        MarqueeTextBlock.TextWrapping = layout.ShouldScroll ? TextWrapping.NoWrap : TextWrapping.Wrap;
        MarqueeTextBlock.HorizontalAlignment = layout.ShouldScroll ? System.Windows.HorizontalAlignment.Left : System.Windows.HorizontalAlignment.Center;
        MarqueeTextBlock.VerticalAlignment = System.Windows.VerticalAlignment.Center;
        MarqueeTextBlock.TextAlignment = layout.ShouldScroll ? TextAlignment.Left : TextAlignment.Center;
        BannerBorder.Padding = layout.ShouldScroll ? new Thickness(0) : new Thickness(48);
        BannerBorder.Opacity = layout.ShouldScroll ? 0.88 : 1;
        BannerViewport.Margin = layout.ShouldScroll ? new Thickness(0, 0, 56, 0) : new Thickness(72);
    }

    private void StopScroll()
    {
        MarqueeTransform.BeginAnimation(TranslateTransform.XProperty, null);
        MarqueeTransform.X = 0;
    }

    private static SolidColorBrush ResolveBrush(string colorName)
    {
        return colorName switch
        {
            "SeaGreen" => System.Windows.Media.Brushes.SeaGreen,
            "MediumPurple" => System.Windows.Media.Brushes.MediumPurple,
            "SlateGray" => System.Windows.Media.Brushes.SlateGray,
            "Orange" => System.Windows.Media.Brushes.Orange,
            "Gold" => System.Windows.Media.Brushes.Gold,
            "Coral" => System.Windows.Media.Brushes.Coral,
            "Tomato" => System.Windows.Media.Brushes.Tomato,
            "Red" => System.Windows.Media.Brushes.Red,
            "DarkRed" => System.Windows.Media.Brushes.DarkRed,
            "OrangeRed" => System.Windows.Media.Brushes.OrangeRed,
            "Crimson" => System.Windows.Media.Brushes.Crimson,
            _ => System.Windows.Media.Brushes.SteelBlue,
        };
    }
}
