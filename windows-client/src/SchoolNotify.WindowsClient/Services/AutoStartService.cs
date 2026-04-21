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
}
