using System.Diagnostics;
using System.IO;
using System.Threading;

namespace SchoolNotify.WindowsClient.Services;

public static class UpgradeWorker
{
    public static void Run(string sourceDir, string targetDir)
    {
        if (string.IsNullOrEmpty(sourceDir) || string.IsNullOrEmpty(targetDir))
            return;

        if (!Directory.Exists(sourceDir))
            return;

        var mainExeName = Path.GetFileName(Environment.ProcessPath ?? "SchoolNotify.WindowsClient.exe");

        var mainProcesses = Process.GetProcessesByName(Path.GetFileNameWithoutExtension(mainExeName));
        foreach (var proc in mainProcesses)
        {
            if (proc.Id == Environment.ProcessId)
                continue;
            proc.WaitForExit(30000);
        }

        Thread.Sleep(2000);

        try
        {
            CopyDirectory(sourceDir, targetDir);
        }
        catch
        {
            return;
        }

        var targetExe = Path.Combine(targetDir, mainExeName);
        if (File.Exists(targetExe))
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = targetExe,
                UseShellExecute = true,
            });
        }
    }

    private static void CopyDirectory(string source, string target)
    {
        Directory.CreateDirectory(target);

        foreach (var file in Directory.GetFiles(source))
        {
            var destFile = Path.Combine(target, Path.GetFileName(file));
            File.Copy(file, destFile, true);
        }

        foreach (var dir in Directory.GetDirectories(source))
        {
            var destDir = Path.Combine(target, Path.GetFileName(dir));
            CopyDirectory(dir, destDir);
        }
    }
}
