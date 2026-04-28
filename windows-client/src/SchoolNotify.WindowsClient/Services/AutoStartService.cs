using Microsoft.Win32;

namespace SchoolNotify.WindowsClient.Services;

public sealed class AutoStartService
{
    private const string RunKeyPath = @"Software\Microsoft\Windows\CurrentVersion\Run";

    public void EnableForCurrentUser(string appName, string executablePath)
    {
        using var key = Registry.CurrentUser.CreateSubKey(RunKeyPath);
        key?.SetValue(appName, AutoStartCommandBuilder.Build(executablePath));
    }

    public void DisableForCurrentUser(string appName)
    {
        using var key = Registry.CurrentUser.OpenSubKey(RunKeyPath, writable: true);
        key?.DeleteValue(appName, throwOnMissingValue: false);
    }

    public void ApplyForCurrentUser(string appName, string executablePath, bool enabled)
    {
        if (enabled)
        {
            EnableForCurrentUser(appName, executablePath);
            return;
        }

        DisableForCurrentUser(appName);
    }
}
