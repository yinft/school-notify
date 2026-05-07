using Xunit;
using System.Runtime.CompilerServices;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class MainWindowLayoutTests
{
    [Fact]
    public void MainWindow_HasScrollableContentAndSettingsEntryPoint()
    {
        var xaml = File.ReadAllText(FindMainWindowXaml());

        Assert.Contains("x:Name=\"MainScrollViewer\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"SettingsPanel\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Content=\"⚙ 通知设置\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"SettingsButtonClicked\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Content=\"刷新二维码\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"RefreshBindingCodeButtonClicked\"", xaml, StringComparison.Ordinal);
        Assert.Contains("ChoicePillRadioButton", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("<ComboBox", xaml, StringComparison.Ordinal);
    }

    [Fact]
    public void BannerOverlay_HasDismissButtonAndTopBannerOpacity()
    {
        var xaml = File.ReadAllText(FindBannerOverlayXaml());

        Assert.Contains("x:Name=\"CloseButton\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"CloseButtonClicked\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"BannerBorder\"", xaml, StringComparison.Ordinal);
    }

    private static string FindMainWindowXaml([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "MainWindow.xaml"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "MainWindow.xaml");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "MainWindow.xaml");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate MainWindow.xaml from test output directory.");
    }

    private static string FindBannerOverlayXaml([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "BannerOverlayWindow.xaml"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "BannerOverlayWindow.xaml");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "BannerOverlayWindow.xaml");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate BannerOverlayWindow.xaml from test output directory.");
    }
}
