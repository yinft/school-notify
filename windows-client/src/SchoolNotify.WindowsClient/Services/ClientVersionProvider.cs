using System.Reflection;

namespace SchoolNotify.WindowsClient.Services;

public static class ClientVersionProvider
{
    public static string CurrentVersion => GetCurrentVersion();

    private static string GetCurrentVersion()
    {
        var assembly = typeof(ClientVersionProvider).Assembly;
        var informationalVersion = assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion;
        if (!string.IsNullOrWhiteSpace(informationalVersion))
        {
            var metadataSeparatorIndex = informationalVersion.IndexOf('+', StringComparison.Ordinal);
            return metadataSeparatorIndex >= 0 ? informationalVersion[..metadataSeparatorIndex] : informationalVersion;
        }

        return assembly.GetName().Version?.ToString(3) ?? "0.0.0";
    }
}
