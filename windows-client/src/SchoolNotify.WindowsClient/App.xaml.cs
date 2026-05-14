using System;
using SchoolNotify.WindowsClient.Services;

namespace SchoolNotify.WindowsClient;

public partial class App : System.Windows.Application
{
    protected override void OnStartup(System.Windows.StartupEventArgs e)
    {
        base.OnStartup(e);

        if (e.Args.Contains("--upgrade"))
        {
            var sourceDir = GetArgValue(e.Args, "--source");
            var targetDir = GetArgValue(e.Args, "--target");
            UpgradeWorker.Run(sourceDir, targetDir);
            Shutdown();
            return;
        }

        var mainWindow = new MainWindow();
        mainWindow.Show();
    }

    private static string GetArgValue(string[] args, string key)
    {
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (string.Equals(args[i], key, StringComparison.OrdinalIgnoreCase))
                return args[i + 1];
        }
        return string.Empty;
    }
}
