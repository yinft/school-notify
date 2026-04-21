using System;
using System.Reflection;
using System.Windows.Media.Animation;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public class NotificationRuntimeTests
{
    [Fact]
    public void ReconnectPolicy_ReturnsBoundedBackoff()
    {
        Assert.Equal(TimeSpan.FromSeconds(2), ReconnectPolicy.GetDelay(1));
        Assert.Equal(TimeSpan.FromSeconds(4), ReconnectPolicy.GetDelay(2));
        Assert.Equal(TimeSpan.FromSeconds(8), ReconnectPolicy.GetDelay(3));
        Assert.Equal(TimeSpan.FromSeconds(30), ReconnectPolicy.GetDelay(99));
    }

    [Fact]
    public void SpeechAnnouncementService_BuildsReadableUrgentText()
    {
        var text = SpeechAnnouncementFormatter.Format(
            title: "紧急通知",
            content: "请立即到操场集合",
            level: "urgent");

        Assert.Equal("紧急通知。紧急通知。请立即到操场集合。", text);
    }

    [Fact]
    public void SpeechAnnouncementService_BuildsReadableNormalText()
    {
        var text = SpeechAnnouncementFormatter.Format(
            title: "普通通知",
            content: "下午两点开会",
            level: "normal");

        Assert.Equal("普通通知。下午两点开会。", text);
    }

    [Fact]
    public void AutoStartCommandBuilder_QuotesExecutablePath()
    {
        var command = AutoStartCommandBuilder.Build("C:\\Program Files\\School Notify\\SchoolNotify.WindowsClient.exe");

        Assert.Equal("\"C:\\Program Files\\School Notify\\SchoolNotify.WindowsClient.exe\"", command);
    }

    [Fact]
    public void TrayBehavior_ShouldMinimizeToTray_WhenWindowCloseRequested()
    {
        var decision = TrayBehavior.ShouldMinimizeToTray(isExplicitExitRequested: false);

        Assert.True(decision);
    }

    [Fact]
    public void TrayBehavior_ShouldAllowExit_WhenExplicitExitRequested()
    {
        var decision = TrayBehavior.ShouldMinimizeToTray(isExplicitExitRequested: true);

        Assert.False(decision);
    }

    [Fact]
    public void BannerScrollAnimationFactory_BuildsInfiniteRightToLeftLoop()
    {
        var assembly = typeof(ReconnectPolicy).Assembly;
        var type = assembly.GetType("SchoolNotify.WindowsClient.Services.BannerScrollAnimationFactory");

        Assert.NotNull(type);

        var method = type!.GetMethod(
            "Build",
            BindingFlags.Public | BindingFlags.Static,
            binder: null,
            types: [typeof(double), typeof(double), typeof(BannerSettings)],
            modifiers: null);

        Assert.NotNull(method);

        var settings = new BannerSettings(160, 24, "SteelBlue", "Orange", "Red", 10);
        var animation = Assert.IsType<DoubleAnimation>(method!.Invoke(null, [320d, 960d, settings]));

        Assert.Equal(320d, animation.From);
        Assert.Equal(-960d, animation.To);
        Assert.Equal(RepeatBehavior.Forever, animation.RepeatBehavior);
        Assert.True(animation.Duration.HasTimeSpan);
        Assert.True(animation.Duration.TimeSpan > TimeSpan.Zero);
    }

    [Fact]
    public void BannerScrollAnimationFactory_UsesConfiguredScrollSpeed()
    {
        var fast = BannerScrollAnimationFactory.Build(320d, 960d, new BannerSettings(320, 24, "SteelBlue", "Orange", "Red", 10));
        var slow = BannerScrollAnimationFactory.Build(320d, 960d, new BannerSettings(80, 24, "SteelBlue", "Orange", "Red", 10));

        Assert.True(fast.Duration.HasTimeSpan);
        Assert.True(slow.Duration.HasTimeSpan);
        Assert.True(fast.Duration.TimeSpan < slow.Duration.TimeSpan);
    }

    [Fact]
    public void BannerOverlayWindow_ExistsInAssemblyWithExpectedProperties()
    {
        var assembly = typeof(ReconnectPolicy).Assembly;
        var type = assembly.GetType("SchoolNotify.WindowsClient.BannerOverlayWindow");

        Assert.NotNull(type);

        var windowType = typeof(System.Windows.Window);
        Assert.True(windowType.IsAssignableFrom(type));

        var topProperty = type.GetProperty("Top", System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
        Assert.NotNull(topProperty);

        var topmostProperty = type.GetProperty("Topmost", System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
        Assert.NotNull(topmostProperty);

        var showMethod = type.GetMethod("ShowNotification", System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance, binder: null, types: [typeof(string), typeof(string), typeof(BannerSettings)], modifiers: null);
        Assert.NotNull(showMethod);

        var hideMethod = type.GetMethod("HideNotification", System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
        Assert.NotNull(hideMethod);
    }
}
