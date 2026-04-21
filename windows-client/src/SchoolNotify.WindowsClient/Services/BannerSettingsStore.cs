using System.IO;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class BannerSettingsStore
{
    private readonly string _settingsPath;

    public BannerSettingsStore(string? settingsPath = null)
    {
        _settingsPath = settingsPath ?? GetSettingsPath();
    }

    public async Task<BannerSettings> LoadAsync(CancellationToken cancellationToken = default)
    {
        var directoryPath = Path.GetDirectoryName(_settingsPath)!;
        Directory.CreateDirectory(directoryPath);

        if (!File.Exists(_settingsPath))
        {
            return BannerSettings.Default;
        }

        await using var stream = File.OpenRead(_settingsPath);
        return await JsonSerializer.DeserializeAsync<BannerSettings>(stream, cancellationToken: cancellationToken)
            ?? BannerSettings.Default;
    }

    public async Task SaveAsync(BannerSettings settings, CancellationToken cancellationToken = default)
    {
        var directoryPath = Path.GetDirectoryName(_settingsPath)!;
        Directory.CreateDirectory(directoryPath);

        await using var stream = File.Create(_settingsPath);
        await JsonSerializer.SerializeAsync(stream, settings, cancellationToken: cancellationToken);
    }

    private static string GetSettingsPath()
    {
        return Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "SchoolNotify",
            "banner-settings.json");
    }
}
