using System.IO;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class ClientSettingsStore
{
    private readonly string _settingsPath;

    public ClientSettingsStore(string? settingsPath = null)
    {
        _settingsPath = settingsPath ?? GetSettingsPath();
    }

    public async Task<ClientSettings> LoadAsync(CancellationToken cancellationToken = default)
    {
        var directoryPath = Path.GetDirectoryName(_settingsPath)!;
        Directory.CreateDirectory(directoryPath);

        if (!File.Exists(_settingsPath))
        {
            return ClientSettings.Default;
        }

        await using var stream = File.OpenRead(_settingsPath);
        return await JsonSerializer.DeserializeAsync<ClientSettings>(stream, cancellationToken: cancellationToken)
            ?? ClientSettings.Default;
    }

    public async Task SaveAsync(ClientSettings settings, CancellationToken cancellationToken = default)
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
            "client-settings.json");
    }
}
