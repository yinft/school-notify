using System.IO;
using System.Text.Json;

namespace SchoolNotify.WindowsClient.Services;

public sealed class ServerConfigStore
{
    private const string DefaultBaseUrl = "http://127.0.0.1:8000";
    private const string EnvVarName = "SCHOOL_NOTIFY_BASE_URL";
    private const string ConfigFileName = "client-config.json";

    public ServerConfig Load()
    {
        var url = Environment.GetEnvironmentVariable(EnvVarName);
        if (!string.IsNullOrWhiteSpace(url))
        {
            return new ServerConfig(url.Trim().TrimEnd('/'));
        }

        var configFile = Path.Combine(AppContext.BaseDirectory, ConfigFileName);
        if (File.Exists(configFile))
        {
            try
            {
                using var stream = File.OpenRead(configFile);
                var config = JsonSerializer.Deserialize<ClientConfig>(stream);
                if (config?.BaseUrl is { Length: > 0 })
                {
                    return new ServerConfig(config.BaseUrl.TrimEnd('/'));
                }
            }
            catch
            {
            }
        }

        return new ServerConfig(DefaultBaseUrl);
    }

    private sealed record ClientConfig(string BaseUrl);
}

public sealed record ServerConfig(string BaseUrl);
