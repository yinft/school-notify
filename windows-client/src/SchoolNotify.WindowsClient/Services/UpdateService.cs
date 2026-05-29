using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class UpdateService
{
    private static readonly string[] RequiredUpdateFiles =
    [
        "SchoolNotify.WindowsClient.exe",
        "SchoolNotify.WindowsClient.dll",
        "SchoolNotify.WindowsClient.runtimeconfig.json",
        "client-config.json",
    ];

    private readonly HttpClient _httpClient;
    private readonly string _installDir;
    private readonly string _updateRootDir;

    private string? _pendingVersion;
    private bool _isDownloading;

    public bool IsUpdatePending => _pendingVersion is not null;

    public bool IsDownloading => _isDownloading;

    public UpdateService(HttpClient httpClient, string installDir, string? updateRootDir = null)
    {
        _httpClient = httpClient;
        _installDir = installDir;
        _updateRootDir = string.IsNullOrWhiteSpace(updateRootDir)
            ? Path.Combine(Path.GetTempPath(), "SchoolNotify", "updates")
            : updateRootDir;
        RestorePendingUpdate();
    }

    private void RestorePendingUpdate()
    {
        if (!Directory.Exists(_updateRootDir))
            return;

        try
        {
            foreach (var dir in Directory.GetDirectories(_updateRootDir))
            {
                var extractDir = Path.Combine(dir, "extracted");
                if (IsCompleteUpdateDirectory(extractDir))
                {
                    _pendingVersion = Path.GetFileName(dir);
                    return;
                }

                Directory.Delete(dir, true);
            }
        }
        catch
        {
        }
    }

    public async Task<bool> TryStartUpdateAsync(DeviceUpdateInfo updateInfo, CancellationToken cancellationToken)
    {
        if (_isDownloading)
            return false;

        if (_pendingVersion == updateInfo.LatestVersion)
            return false;

        if (string.IsNullOrEmpty(updateInfo.DownloadUrl) || string.IsNullOrEmpty(updateInfo.LatestVersion))
            return false;

        if (!Uri.TryCreate(updateInfo.DownloadUrl, UriKind.Absolute, out var downloadUri))
            return false;

        var versionDir = Path.Combine(_updateRootDir, updateInfo.LatestVersion);
        var extractDir = Path.Combine(versionDir, "extracted");
        var extractingDir = Path.Combine(versionDir, "extracting");

        if (IsCompleteUpdateDirectory(extractDir))
        {
            _pendingVersion = updateInfo.LatestVersion;
            return true;
        }

        _isDownloading = true;

        try
        {
            if (IsCompleteUpdateDirectory(extractDir))
            {
                _pendingVersion = updateInfo.LatestVersion;
                return true;
            }

            var zipPath = Path.Combine(versionDir, "update.zip");

            CleanOldUpdateDirs(updateInfo.LatestVersion);

            if (Directory.Exists(extractingDir))
                Directory.Delete(extractingDir, true);
            if (Directory.Exists(extractDir))
                Directory.Delete(extractDir, true);

            Directory.CreateDirectory(extractingDir);

            await DownloadFileAsync(downloadUri, zipPath, cancellationToken);

            ZipFile.ExtractToDirectory(zipPath, extractingDir, true);
            if (!IsCompleteUpdateDirectory(extractingDir))
            {
                Directory.Delete(extractingDir, true);
                return false;
            }

            Directory.Move(extractingDir, extractDir);

            _pendingVersion = updateInfo.LatestVersion;
            return true;
        }
        catch (OperationCanceledException)
        {
            return false;
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Update download failed: {ex.Message}");
            return false;
        }
        finally
        {
            _isDownloading = false;
        }
    }

    public void ApplyUpdateAndRestart()
    {
        if (_pendingVersion is null)
            return;

        var extractDir = Path.Combine(_updateRootDir, _pendingVersion, "extracted");
        if (!IsCompleteUpdateDirectory(extractDir))
            return;

        var exePath = Environment.ProcessPath;
        if (string.IsNullOrEmpty(exePath))
            return;

        var workerDir = PrepareUpgradeWorkerDir(exePath);
        var workerExePath = Path.Combine(workerDir, Path.GetFileName(exePath));
        if (!File.Exists(workerExePath))
            return;

        var args = $"--upgrade --source \"{extractDir.TrimEnd('\\')}\" --target \"{_installDir.TrimEnd('\\')}\"";
        Process.Start(new ProcessStartInfo
        {
            FileName = workerExePath,
            Arguments = args,
            UseShellExecute = true,
            WindowStyle = ProcessWindowStyle.Hidden,
        });

        System.Windows.Application.Current.Shutdown();
    }

    private string PrepareUpgradeWorkerDir(string exePath)
    {
        var sourceDir = Path.GetDirectoryName(exePath);
        if (string.IsNullOrEmpty(sourceDir))
            return string.Empty;

        var workerDir = Path.Combine(_updateRootDir, "worker");
        if (Directory.Exists(workerDir))
            Directory.Delete(workerDir, true);

        CopyDirectory(sourceDir, workerDir);
        return workerDir;
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

    private void CleanOldUpdateDirs(string? keepVersion)
    {
        if (!Directory.Exists(_updateRootDir))
            return;

        try
        {
            foreach (var dir in Directory.GetDirectories(_updateRootDir))
            {
                var dirName = Path.GetFileName(dir);
                if (keepVersion is not null && dirName == keepVersion)
                    continue;

                Directory.Delete(dir, true);
            }
        }
        catch
        {
        }
    }

    private async Task DownloadFileAsync(Uri url, string destinationPath, CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var contentStream = await response.Content.ReadAsStreamAsync(cancellationToken);
        await using var fileStream = File.Create(destinationPath);
        await contentStream.CopyToAsync(fileStream, cancellationToken);
    }

    private static bool IsCompleteUpdateDirectory(string directory)
    {
        if (!Directory.Exists(directory))
            return false;

        return RequiredUpdateFiles.All(fileName => File.Exists(Path.Combine(directory, fileName)));
    }
}
