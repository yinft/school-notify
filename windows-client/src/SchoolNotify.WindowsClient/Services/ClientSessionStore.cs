using System.IO;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class ClientSessionStore
{
    private readonly string _sessionPath;

    private readonly Func<string> _getCurrentVersion;

    public ClientSessionStore(string? sessionPath = null, Func<string>? getCurrentVersion = null)
    {
        _sessionPath = string.IsNullOrWhiteSpace(sessionPath) ? GetDefaultSessionPath() : sessionPath;
        _getCurrentVersion = getCurrentVersion ?? (() => ClientVersionProvider.CurrentVersion);
    }

    public async Task<ClientSession> LoadOrCreateAsync(CancellationToken cancellationToken = default)
    {
        var sessionPath = _sessionPath;
        var directoryPath = Path.GetDirectoryName(sessionPath)!;
        Directory.CreateDirectory(directoryPath);

        if (File.Exists(sessionPath))
        {
            ClientSession? existing;
            await using (var existingStream = File.OpenRead(sessionPath))
            {
                existing = await JsonSerializer.DeserializeAsync<ClientSession>(existingStream, cancellationToken: cancellationToken);
            }

            if (existing is not null)
            {
                var currentVersion = _getCurrentVersion();
                if (existing.ClientVersion == currentVersion)
                {
                    return existing;
                }

                var updated = existing with { ClientVersion = currentVersion };
                await SaveAsync(updated, cancellationToken);
                return updated;
            }
        }

        var session = new ClientSession(
            DeviceId: Guid.NewGuid().ToString("N"),
            DeviceName: Environment.MachineName,
            ClientVersion: _getCurrentVersion());

        await using var createStream = File.Create(sessionPath);
        await JsonSerializer.SerializeAsync(createStream, session, cancellationToken: cancellationToken);
        return session;
    }

    public async Task SaveAsync(ClientSession session, CancellationToken cancellationToken = default)
    {
        var directoryPath = Path.GetDirectoryName(_sessionPath)!;
        Directory.CreateDirectory(directoryPath);
        await using var stream = File.Create(_sessionPath);
        await JsonSerializer.SerializeAsync(stream, session, cancellationToken: cancellationToken);
    }

    private static string GetDefaultSessionPath()
    {
        return Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "SchoolNotify",
            "client-session.json");
    }
}
