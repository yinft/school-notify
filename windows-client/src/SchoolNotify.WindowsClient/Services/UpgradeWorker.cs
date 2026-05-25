using System.Diagnostics;
using System.IO;
using System.Threading;

namespace SchoolNotify.WindowsClient.Services;

public static class UpgradeWorker
{
    private static readonly string LogPath = Path.Combine(Path.GetTempPath(), "SchoolNotify", "updates", "upgrade.log");

    public static void Run(string sourceDir, string targetDir)
    {
        sourceDir = StripQuotes(sourceDir);
        targetDir = StripQuotes(targetDir);
        try
        {
            Log($"UpgradeWorker started. sourceDir=[{sourceDir}] targetDir=[{targetDir}]");

            if (string.IsNullOrEmpty(sourceDir) || string.IsNullOrEmpty(targetDir))
            {
                Log("Exiting: sourceDir or targetDir is empty.");
                return;
            }

            if (!Directory.Exists(sourceDir))
            {
                Log($"Exiting: sourceDir does not exist: {sourceDir}");
                return;
            }

            var mainExeName = Path.GetFileName(Environment.ProcessPath ?? "SchoolNotify.WindowsClient.exe");
            Log($"mainExeName=[{mainExeName}] ProcessId=[{Environment.ProcessId}]");

            var mainProcesses = Process.GetProcessesByName(Path.GetFileNameWithoutExtension(mainExeName));
            Log($"Found {mainProcesses.Length} processes with name {Path.GetFileNameWithoutExtension(mainExeName)}");

            foreach (var proc in mainProcesses)
            {
                if (proc.Id == Environment.ProcessId)
                    continue;

                Log($"Waiting for process {proc.Id} to exit (max 30s)...");
                proc.WaitForExit(30000);
                Log($"Process {proc.Id} exited or timed out. HasExited={proc.HasExited}");
            }

            Thread.Sleep(2000);

            Log($"Cleaning target directory [{targetDir}] before copy");
            CleanTargetDirectory(sourceDir, targetDir);

            Log($"Starting file copy from [{sourceDir}] to [{targetDir}]");
            CopyDirectoryWithRetry(sourceDir, targetDir, maxRetries: 5, retryDelayMs: 2000);
            Log("File copy completed.");

            var targetExe = Path.Combine(targetDir, mainExeName);
            if (File.Exists(targetExe))
            {
                Log($"Starting new version: {targetExe}");
                Process.Start(new ProcessStartInfo
                {
                    FileName = targetExe,
                    UseShellExecute = true,
                });
            }
            else
            {
                Log($"ERROR: target exe not found: {targetExe}");
            }
        }
        catch (Exception ex)
        {
            Log($"EXCEPTION: {ex.GetType().Name}: {ex.Message}\n{ex.StackTrace}");
        }
    }

    private static string StripQuotes(string value)
    {
        if (value.Length >= 2 && value.StartsWith('"') && value.EndsWith('"'))
            return value[1..^1];
        return value;
    }

    private static void Log(string message)
    {
        try
        {
            var dir = Path.GetDirectoryName(LogPath);
            if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                Directory.CreateDirectory(dir);

            File.AppendAllText(LogPath, $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff}] {message}\n");
        }
        catch
        {
        }
    }

    private static void CopyDirectoryWithRetry(string source, string target, int maxRetries, int retryDelayMs)
    {
        for (int attempt = 1; attempt <= maxRetries; attempt++)
        {
            try
            {
                CopyDirectory(source, target);
                return;
            }
            catch (IOException ex) when (attempt < maxRetries)
            {
                Log($"Copy attempt {attempt} failed: {ex.Message}. Retrying in {retryDelayMs}ms...");
                Thread.Sleep(retryDelayMs);
            }
        }
    }

    private static void CleanTargetDirectory(string source, string target)
    {
        if (!Directory.Exists(target))
        {
            return;
        }

        var sourceFiles = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        CollectRelativePaths(source, source, sourceFiles);

        foreach (var file in Directory.GetFiles(target, "*", SearchOption.AllDirectories))
        {
            var relative = file.Substring(target.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (!sourceFiles.Contains(relative))
            {
                try
                {
                    File.Delete(file);
                    Log($"Removed old file: {relative}");
                }
                catch (Exception ex)
                {
                    Log($"Failed to remove old file {relative}: {ex.Message}");
                }
            }
        }

        foreach (var dir in Directory.GetDirectories(target, "*", SearchOption.TopDirectoryOnly))
        {
            var dirName = Path.GetFileName(dir);
            var sourceDir = Path.Combine(source, dirName);
            if (!Directory.Exists(sourceDir))
            {
                try
                {
                    Directory.Delete(dir, true);
                    Log($"Removed old directory: {dirName}");
                }
                catch (Exception ex)
                {
                    Log($"Failed to remove old directory {dirName}: {ex.Message}");
                }
            }
        }
    }

    private static void CollectRelativePaths(string root, string current, HashSet<string> results)
    {
        foreach (var file in Directory.GetFiles(current))
        {
            var relative = file.Substring(root.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            results.Add(relative);
        }

        foreach (var dir in Directory.GetDirectories(current))
        {
            CollectRelativePaths(root, dir, results);
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
