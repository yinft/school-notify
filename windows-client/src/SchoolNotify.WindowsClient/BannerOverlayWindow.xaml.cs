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
        MarqueeTextBlock.Text = text;
        MarqueeTextBlock.FontSize = settings.FontSize;
        BannerBorder.Background = ResolveBrush(colorName);
        Visibility = Visibility.Visible;
        UpdateLayout();
        StartScroll(settings);
    }

    public void HideNotification()
    {
        StopScroll();
        Visibility = Visibility.Collapsed;
    }

    private void StartScroll(BannerSettings settings)
    {
        var animation = BannerScrollAnimationFactory.Build(
            BannerViewport.ActualWidth,
            MarqueeTextBlock.ActualWidth,
            settings);

        MarqueeTransform.BeginAnimation(TranslateTransform.XProperty, animation, HandoffBehavior.SnapshotAndReplace);
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
