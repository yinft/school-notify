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
    public void MainWindow_UsesPolishedCardDashboardStyling()
    {
        var xaml = File.ReadAllText(FindMainWindowXaml());

        Assert.Contains("MinHeight=\"640\"", xaml, StringComparison.Ordinal);
        Assert.Contains("MinWidth=\"920\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Key=\"CardBorder\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Key=\"SectionTitle\"", xaml, StringComparison.Ordinal);
        Assert.Contains("DropShadowEffect", xaml, StringComparison.Ordinal);
        Assert.Contains("Source=\"pack://application:,,,/Assets/brand-speaker.png\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Text=\"设备运行状态\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Text=\"小程序绑定\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Text=\"使用提示\"", xaml, StringComparison.Ordinal);
        Assert.Contains("#FFF7ED", xaml, StringComparison.Ordinal);
        Assert.Contains("#F97316", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("Background=\"#0F172A\"", xaml, StringComparison.Ordinal);
        Assert.Contains("CornerRadius=\"12\"", xaml, StringComparison.Ordinal);
        Assert.DoesNotContain("Text=\"喇\"", xaml, StringComparison.Ordinal);
    }

    [Fact]
    public void ClientProject_ConfiguresApplicationIcon()
    {
        var projectPath = FindClientProjectFile();
        var project = File.ReadAllText(projectPath);
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());
        var updateServiceCode = File.ReadAllText(FindUpdateServiceCode());
        var assetsPath = Path.Combine(Path.GetDirectoryName(projectPath)!, "Assets");
        var iconPath = Path.Combine(assetsPath, "app.ico");
        var brandImagePath = Path.Combine(assetsPath, "brand-speaker.png");

        Assert.Contains("<ApplicationIcon>Assets\\app.ico</ApplicationIcon>", project, StringComparison.Ordinal);
        Assert.Contains("<Resource Include=\"Assets\\app.ico\" />", project, StringComparison.Ordinal);
        Assert.Contains("<Resource Include=\"Assets\\brand-speaker.png\" />", project, StringComparison.Ordinal);
        Assert.Contains("LoadTrayIcon()", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Application.GetResourceStream", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Text = \"思故桌面小喇叭\"", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Timeout = TimeSpan.FromSeconds(10)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Interval = TimeSpan.FromMinutes(10)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("Interval = TimeSpan.FromMinutes(60)", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("Interval = TimeSpan.FromSeconds(30)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("UpdateCheckTimerOnTick", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("CheckForUpdateAsync", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("_isHeartbeatInProgress", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("_ = TryApplyUpdateAsync(update)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("发现新版本", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("!_updateService.IsDownloading", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("await TryApplyUpdateAsync(update)", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("实时连接：已连接", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("重连状态", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("ShowBalloonTip(2000, \"思故桌面小喇叭\"", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("校园通知屏客户端", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("System.Drawing.SystemIcons.Application", mainWindowCode, StringComparison.Ordinal);
        Assert.DoesNotContain("Task.Delay", updateServiceCode, StringComparison.Ordinal);
        Assert.DoesNotContain("Random", updateServiceCode, StringComparison.Ordinal);
        Assert.DoesNotContain("7201", updateServiceCode, StringComparison.Ordinal);
        Assert.True(File.Exists(iconPath), $"Expected app icon at {iconPath}");
        Assert.True(File.Exists(brandImagePath), $"Expected brand image at {brandImagePath}");
    }

    [Fact]
    public void MainWindow_PrioritizesPendingUpdateStatusBeforeDownloadingStatus()
    {
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());

        var pendingStatusIndex = mainWindowCode.IndexOf("if (_updateService.IsUpdatePending)", StringComparison.Ordinal);
        var availableStatusIndex = mainWindowCode.IndexOf("if (update.Available)", StringComparison.Ordinal);

        Assert.True(pendingStatusIndex >= 0);
        Assert.True(availableStatusIndex >= 0);
        Assert.True(pendingStatusIndex < availableStatusIndex);
    }

    [Fact]
    public void MainWindow_BalloonTipClickDoesNotImmediatelyApplyUpdate()
    {
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());

        Assert.DoesNotContain("BalloonTipClicked += (_, _) => RestartForUpdate();", mainWindowCode, StringComparison.Ordinal);
        Assert.Contains("BalloonTipClicked += (_, _) => RestoreFromTray();", mainWindowCode, StringComparison.Ordinal);
    }

    [Fact]
    public void UpdateService_RestartForUpdate_SetsExplicitExitFlag()
    {
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());

        var restartIndex = mainWindowCode.IndexOf("private void RestartForUpdate()", StringComparison.Ordinal);
        Assert.True(restartIndex >= 0, "Could not find RestartForUpdate method");

        var methodBody = mainWindowCode.Substring(restartIndex);
        var braceStart = methodBody.IndexOf('{');
        var braceEnd = methodBody.IndexOf('}', braceStart);
        var body = methodBody.Substring(braceStart, braceEnd - braceStart + 1);

        Assert.Contains("_isExplicitExitRequested = true", body, StringComparison.Ordinal);
    }

    [Fact]
    public void MainWindow_RestartForUpdate_ShowsProgressWindowBeforeUpdate()
    {
        var mainWindowCode = File.ReadAllText(FindMainWindowCodeBehind());

        var restartIndex = mainWindowCode.IndexOf("private void RestartForUpdate()", StringComparison.Ordinal);
        Assert.True(restartIndex >= 0, "Could not find RestartForUpdate method");

        var methodBody = mainWindowCode.Substring(restartIndex);
        var braceStart = methodBody.IndexOf('{');
        var braceEnd = methodBody.IndexOf('}', braceStart);
        var body = methodBody.Substring(braceStart, braceEnd - braceStart + 1);

        var progressIndex = body.IndexOf("UpdateProgressWindow", StringComparison.Ordinal);
        var applyIndex = body.IndexOf("ApplyUpdateAndRestart", StringComparison.Ordinal);
        Assert.True(progressIndex >= 0, "RestartForUpdate should reference UpdateProgressWindow");
        Assert.True(applyIndex >= 0, "RestartForUpdate should call ApplyUpdateAndRestart");
        Assert.True(progressIndex < applyIndex, "Progress window should be shown before ApplyUpdateAndRestart");
    }

    [Fact]
    public void UpdateProgressWindow_HasIndeterminateProgressAndUpgradeMessage()
    {
        var xamlPath = FindUpdateProgressWindowXaml();
        var xaml = File.ReadAllText(xamlPath);

        Assert.Contains("IsIndeterminate=\"True\"", xaml, StringComparison.Ordinal);
        Assert.Contains("正在升级", xaml, StringComparison.Ordinal);
        Assert.Contains("Topmost=\"True\"", xaml, StringComparison.Ordinal);
        Assert.Contains("WindowStartupLocation=\"CenterScreen\"", xaml, StringComparison.Ordinal);
        Assert.Contains("WindowStyle=\"None\"", xaml, StringComparison.Ordinal);
    }

    [Fact]
    public void UpdateService_LaunchesUpgradeWorkerFromTemporaryWorkerDirectory()
    {
        var updateServiceCode = File.ReadAllText(FindUpdateServiceCode());

        Assert.Contains("PrepareUpgradeWorkerDir", updateServiceCode, StringComparison.Ordinal);
        Assert.Contains("var workerExePath = Path.Combine(workerDir, Path.GetFileName(exePath));", updateServiceCode, StringComparison.Ordinal);
        Assert.Contains("FileName = workerExePath", updateServiceCode, StringComparison.Ordinal);
        Assert.DoesNotContain("FileName = exePath", updateServiceCode, StringComparison.Ordinal);
    }

    [Fact]
    public void UpgradeWorker_CopiesFullUpdatePackage()
    {
        var upgradeWorkerCode = File.ReadAllText(FindUpgradeWorkerCode());

        Assert.Contains("CopyDirectoryWithRetry", upgradeWorkerCode, StringComparison.Ordinal);
        Assert.Contains("foreach (var dir in Directory.GetDirectories(source))", upgradeWorkerCode, StringComparison.Ordinal);
        Assert.DoesNotContain("ShouldCopyAppFile", upgradeWorkerCode, StringComparison.Ordinal);
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

    private static string FindUpgradeWorkerCode([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "Services",
            "UpgradeWorker.cs"));
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
            "UpgradeWorker.cs");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "Services", "UpgradeWorker.cs");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate UpgradeWorker.cs from test output directory.");
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

    private static string FindUpdateProgressWindowXaml([CallerFilePath] string sourceFilePath = "")
    {
        var sourceRelativePath = Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(sourceFilePath)!,
            "..",
            "..",
            "src",
            "SchoolNotify.WindowsClient",
            "UpdateProgressWindow.xaml"));
        if (File.Exists(sourceRelativePath))
        {
            return sourceRelativePath;
        }

        var workingDirectoryPath = Path.Combine(
            Environment.CurrentDirectory,
            "windows-client",
            "src",
            "SchoolNotify.WindowsClient",
            "UpdateProgressWindow.xaml");
        if (File.Exists(workingDirectoryPath))
        {
            return workingDirectoryPath;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var path = Path.Combine(directory.FullName, "src", "SchoolNotify.WindowsClient", "UpdateProgressWindow.xaml");
            if (File.Exists(path))
            {
                return path;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException("Could not locate UpdateProgressWindow.xaml from test output directory.");
    }
}
