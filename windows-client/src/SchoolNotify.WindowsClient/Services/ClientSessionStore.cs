using System.IO;
using System.Text.Json;
using SchoolNotify.WindowsClient.Models;

namespace SchoolNotify.WindowsClient.Services;

public sealed class ClientSessionStore
{
    private const string CurrentVersion = "0.1.0";

    public async Task<ClientSession> LoadOrCreateAsync(CancellationToken cancellationToken = default)
    {
        var sessionPath = GetSessionPath();
        var directoryPath = Path.GetDirectoryName(sessionPath)!;
        Directory.CreateDirectory(directoryPath);

        if (File.Exists(sessionPath))
        {
            await using var existingStream = File.OpenRead(sessionPath);
            var existing = await JsonSerializer.DeserializeAsync<ClientSession>(existingStream, cancellationToken: cancellationToken);
            if (existing is not null)
            {
                return existing;
            }
        }

        var session = new ClientSession(
            DeviceId: Guid.NewGuid().ToString("N"),
            DeviceName: Environment.MachineName,
            ClientVersion: CurrentVersion);

        await using var createStream = File.Create(sessionPath);
        await JsonSerializer.SerializeAsync(createStream, session, cancellationToken: cancellationToken);
        return session;
    }

    private static string GetSessionPath()
    {
        return Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "SchoolNotify",
            "client-session.json");
    }
}
