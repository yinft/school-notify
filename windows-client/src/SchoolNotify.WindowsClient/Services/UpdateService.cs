using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class UpdateService
{
    private readonly HttpClient _httpClient;
    private readonly string _installDir;
    private readonly Random _random = new();
    private readonly string _updateRootDir;

    private string? _pendingVersion;
    private bool _isDownloading;

    public bool IsUpdatePending => _pendingVersion is not null;

    public UpdateService(HttpClient httpClient, string installDir)
    {
        _httpClient = httpClient;
        _installDir = installDir;
        _updateRootDir = Path.Combine(Path.GetTempPath(), "SchoolNotify", "updates");
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
                if (Directory.Exists(extractDir) && Directory.GetFiles(extractDir).Length > 0)
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

        var versionDir = Path.Combine(_updateRootDir, updateInfo.LatestVersion);
        var extractDir = Path.Combine(versionDir, "extracted");

        if (Directory.Exists(extractDir) && Directory.GetFiles(extractDir).Length > 0)
        {
            _pendingVersion = updateInfo.LatestVersion;
            return true;
        }

        _isDownloading = true;

        try
        {
            int delaySeconds = _random.Next(0, 7201);
            await Task.Delay(TimeSpan.FromSeconds(delaySeconds), cancellationToken);

            if (Directory.Exists(extractDir) && Directory.GetFiles(extractDir).Length > 0)
            {
                _pendingVersion = updateInfo.LatestVersion;
                return true;
            }

            var zipPath = Path.Combine(versionDir, "update.zip");

            CleanOldUpdateDirs(updateInfo.LatestVersion);

            Directory.CreateDirectory(extractDir);

            await DownloadFileAsync(updateInfo.DownloadUrl, zipPath, cancellationToken);

            ZipFile.ExtractToDirectory(zipPath, extractDir, true);

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
        if (!Directory.Exists(extractDir))
            return;

        var exePath = Environment.ProcessPath;
        if (string.IsNullOrEmpty(exePath))
            return;

        var args = $"--upgrade --source \"{extractDir}\" --target \"{_installDir}\"";
        Process.Start(new ProcessStartInfo
        {
            FileName = exePath,
            Arguments = args,
            UseShellExecute = true,
        });

        System.Windows.Application.Current.Shutdown();
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

    private async Task DownloadFileAsync(string url, string destinationPath, CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var contentStream = await response.Content.ReadAsStreamAsync(cancellationToken);
        await using var fileStream = File.Create(destinationPath);
        await contentStream.CopyToAsync(fileStream, cancellationToken);
    }
}
