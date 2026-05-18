using Xunit;
using System.Runtime.CompilerServices;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class MainWindowLayoutTests
{
    [Fact]
    public void MainWindow_HasScrollableContentAndSettingsEntryPoint()
    {
        var xaml = File.ReadAllText(FindMainWindowXaml());

        Assert.Contains("Title=\"思故桌面小喇叭\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Text=\"思故桌面小喇叭\"", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("School Notify Client", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("校园通知屏客户端", xaml, StringComparison.Ordinal);
        Assert.Contains("Icon=\"pack://application:,,,/Assets/app.ico\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"MainScrollViewer\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"SettingsPanel\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"ClientVersionTextBlock\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"UpdateStatusTextBlock\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Text=\"实时连接：未启动\"", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("重连状态", xaml, StringComparison.Ordinal);
        Assert.Contains("Content=\"⚙ 通知设置\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"SettingsButtonClicked\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Content=\"刷新二维码\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"RefreshBindingCodeButtonClicked\"", xaml, StringComparison.Ordinal);
        Assert.Contains("ChoicePillRadioButton", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("<ComboBox", xaml, StringComparison.Ordinal);
    }

    [Fact]
    public void ClientProject_ConfiguresApplicationIcon()
    {
        var projectPath = FindClientProjectFile();
        var project = File.ReadAllText(projectPath);
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());
        var updateServiceCode = File.ReadAllText(FindUpdateServiceCode());
        var iconPath = Path.Combine(Path.GetDirectoryName(projectPath)!, "Assets", "app.ico");

        Assert.Contains("<ApplicationIcon>Assets\\app.ico</ApplicationIcon>", project, StringComparison.Ordinal);
        Assert.Contains("<Resource Include=\"Assets\\app.ico\" />", project, StringComparison.Ordinal);
        Assert.Contains("LoadTrayIcon()", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Application.GetResourceStream", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Text = \"思故桌面小喇叭\"", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Timeout = TimeSpan.FromSeconds(10)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("_isHeartbeatInProgress", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("_ = TryApplyUpdateAsync(heartbeat.Update)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("发现新版本", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("!_updateService.IsDownloading", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("await TryApplyUpdateAsync(heartbeat.Update)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("实时连接：已连接", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("重连状态", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("ShowBalloonTip(2000, \"思故桌面小喇叭\"", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("校园通知屏客户端", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("System.Drawing.SystemIcons.Application", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("Task.Delay", updateServiceCode, StringComparison.Ordinal);
        Assert.DoesNotContain("Random", updateServiceCode, StringComparison.Ordinal);
        Assert.DoesNotContain("7201", updateServiceCode, StringComparison.Ordinal);
        Assert.True(File.Exists(iconPath), $"Expected app icon at {iconPath}");
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

    private static string FindMainWindowCodeBehind([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "MainWindow.xaml.cs"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "MainWindow.xaml.cs");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "MainWindow.xaml.cs");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate MainWindow.xaml.cs from test output directory.");
    }

    private static string FindUpdateServiceCode([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "Services",
            "UpdateService.cs"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "Services",
            "UpdateService.cs");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "Services", "UpdateService.cs");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate UpdateService.cs from test output directory.");
    }

    private static string FindClientProjectFile([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "SchoolNotify.WindowsClient.csproj"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "SchoolNotify.WindowsClient.csproj");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "SchoolNotify.WindowsClient.csproj");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate SchoolNotify.WindowsClient.csproj from test output directory.");
    }
}
