using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class MainWindowLayoutTests
{
    [Fact]
    public void MainWindow_HasScrollableContentAndSettingsEntryPoint()
    {
        var xaml = File.ReadAllText(FindMainWindowXaml());

        Assert.Contains("x:Name=\"MainScrollViewer\"", xaml, StringComparison.Ordinal);
        Assert.Contains("x:Name=\"SettingsPanel\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Content=\"设置\"", xaml, StringComparison.Ordinal);
        Assert.Contains("Click=\"SettingsButtonClicked\"", xaml, StringComparison.Ordinal);
    }

    private static string FindMainWindowXaml()
    {
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
}
