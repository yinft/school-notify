using System.IO.Compression;
using System.Net;
using System.Net.Http;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class UpdateServiceTests
{
    [Fact]
    public async Task TryStartUpdateAsync_RejectsRelativeDownloadUrl()
    {
        var handler = new RecordingHandler();
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("https://api.example.test")
        };
        var installDir = Path.Combine(Path.GetTempPath(), $"school-notify-install-{Guid.NewGuid():N}");
        var service = new UpdateService(httpClient, installDir);

        var started = await service.TryStartUpdateAsync(
            new DeviceUpdateInfo(
                Available: true,
                CurrentVersion: "0.1.0",
                LatestVersion: "0.2.0",
                DownloadUrl: "/cdn/windows-client.zip"),
            CancellationToken.None);

        Assert.False(started);
        Assert.Null(handler.LastRequestUri);
    }

    [Fact]
    public async Task TryStartUpdateAsync_UsesAbsoluteDownloadUrlWithoutBackendBaseAddress()
    {
        var handler = new RecordingHandler(CreateZipBytes());
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("https://api.example.test")
        };
        var installDir = Path.Combine(Path.GetTempPath(), $"school-notify-install-{Guid.NewGuid():N}");
        var updateRootDir = Path.Combine(Path.GetTempPath(), $"school-notify-test-updates-{Guid.NewGuid():N}");
        var service = new UpdateService(httpClient, installDir, updateRootDir);
        var latestVersion = $"9.9.{Random.Shared.Next(1000, 9999)}";

        var started = await service.TryStartUpdateAsync(
            new DeviceUpdateInfo(
                Available: true,
                CurrentVersion: "0.1.0",
                LatestVersion: latestVersion,
                DownloadUrl: "https://cdn.example.test/windows-client.zip"),
            CancellationToken.None);

        Assert.True(started);
        Assert.Equal("https://cdn.example.test/windows-client.zip", handler.LastRequestUri?.ToString());
        Assert.True(Directory.Exists(Path.Combine(updateRootDir, latestVersion, "extracted")));
    }

    [Fact]
    public void Constructor_DoesNotRestoreIncompletePendingUpdate()
    {
        using var temp = new TempDirectory();
        var versionDir = Path.Combine(temp.Path, "1.0.1");
        var extractedDir = Path.Combine(versionDir, "extracted");
        Directory.CreateDirectory(extractedDir);
        File.WriteAllText(Path.Combine(extractedDir, "SchoolNotify.WindowsClient.exe"), "fake exe");

        var service = new UpdateService(new HttpClient(new RecordingHandler()), temp.Path, temp.Path);

        Assert.False(service.IsUpdatePending);
        Assert.False(Directory.Exists(versionDir));
    }

    [Fact]
    public void Constructor_RestoresCompletePendingUpdate()
    {
        using var temp = new TempDirectory();
        var extractedDir = Path.Combine(temp.Path, "1.0.1", "extracted");
        Directory.CreateDirectory(extractedDir);
        WriteRequiredUpdateFiles(extractedDir);

        var service = new UpdateService(new HttpClient(new RecordingHandler()), temp.Path, temp.Path);

        Assert.True(service.IsUpdatePending);
    }

    private static byte[] CreateZipBytes()
    {
        using var stream = new MemoryStream();
        using (var archive = new ZipArchive(stream, ZipArchiveMode.Create, leaveOpen: true))
        {
            foreach (var fileName in RequiredUpdateFiles)
            {
                var entry = archive.CreateEntry(fileName);
                using var entryStream = entry.Open();
                using var writer = new StreamWriter(entryStream);
                writer.Write(fileName);
            }
        }

        return stream.ToArray();
    }

    private static readonly string[] RequiredUpdateFiles =
    [
        "SchoolNotify.WindowsClient.exe",
        "SchoolNotify.WindowsClient.dll",
        "SchoolNotify.WindowsClient.runtimeconfig.json",
        "client-config.json",
    ];

    private static void WriteRequiredUpdateFiles(string directory)
    {
        foreach (var fileName in RequiredUpdateFiles)
        {
            File.WriteAllText(Path.Combine(directory, fileName), fileName);
        }
    }

    private sealed class TempDirectory : IDisposable
    {
        public TempDirectory()
        {
            Path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), $"school-notify-update-test-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public void Dispose()
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, true);
            }
        }
    }

    private sealed class RecordingHandler(byte[]? responseBytes = null) : HttpMessageHandler
    {
        public Uri? LastRequestUri { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            LastRequestUri = request.RequestUri;
            var response = new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new ByteArrayContent(responseBytes ?? [])
            };
            return Task.FromResult(response);
        }
    }
}
