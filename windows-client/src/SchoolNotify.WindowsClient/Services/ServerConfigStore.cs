namespace SchoolNotify.WindowsClient.Services;

public sealed class ServerConfigStore
{
    private const string DefaultBaseUrl = "http://127.0.0.1:8000";
    private const string EnvVarName = "SCHOOL_NOTIFY_BASE_URL";

    public ServerConfig Load()
    {
        var url = Environment.GetEnvironmentVariable(EnvVarName);
        if (string.IsNullOrWhiteSpace(url))
        {
            return new ServerConfig(DefaultBaseUrl);
        }

        return new ServerConfig(url.Trim().TrimEnd('/'));
    }
}

public sealed record ServerConfig(string BaseUrl);
