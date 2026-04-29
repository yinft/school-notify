using System.IO;
using System.Text.Json;

namespace SchoolNotify.WindowsClient.Services;

public sealed class ServerConfigStore
{
    private const string DefaultBaseUrl = "http://127.0.0.1:8000";

    private readonly string _configPath;

    public ServerConfigStore(string? configPath = null)
    {
        _configPath = configPath ?? Path.Combine(AppContext.BaseDirectory, "server-config.json");
    }

    public async Task<ServerConfig> LoadAsync(CancellationToken cancellationToken = default)
    {
        if (!File.Exists(_configPath))
        {
            return new ServerConfig(DefaultBaseUrl);
        }

        await using var stream = File.OpenRead(_configPath);
        var config = await JsonSerializer.DeserializeAsync<ServerConfig>(stream, cancellationToken: cancellationToken);
        if (config is null || string.IsNullOrWhiteSpace(config.BaseUrl))
        {
            return new ServerConfig(DefaultBaseUrl);
        }

        return new ServerConfig(config.BaseUrl.Trim().TrimEnd('/'));
    }
}

public sealed record ServerConfig(string BaseUrl);
