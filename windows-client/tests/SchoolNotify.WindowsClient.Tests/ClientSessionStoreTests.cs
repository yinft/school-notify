using System;
using System.IO;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class ClientSessionStoreTests
{
    [Fact]
    public async Task ClientSessionStore_RoundTripsSavedDeviceToken()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-client-session-{Guid.NewGuid():N}.json");

        try
        {
            var store = new ClientSessionStore(filePath);
            var expected = new ClientSession(
                DeviceId: "device-001",
                DeviceName: "值班室电脑",
                ClientVersion: "0.1.0",
                DeviceToken: "device-token-001");

            await store.SaveAsync(expected);
            var actual = await store.LoadOrCreateAsync();

            Assert.Equal(expected, actual);
        }
        finally
        {
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
        }
    }

    [Fact]
    public async Task LoadOrCreateAsync_UpdatesPersistedClientVersionToCurrentVersion()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-client-session-{Guid.NewGuid():N}.json");

        try
        {
            var store = new ClientSessionStore(filePath, () => "0.2.0");
            var saved = new ClientSession(
                DeviceId: "device-001",
                DeviceName: "值班室电脑",
                ClientVersion: "0.1.0",
                DeviceToken: "device-token-001");

            await store.SaveAsync(saved);
            var loaded = await store.LoadOrCreateAsync();
            var reloaded = await store.LoadOrCreateAsync();

            Assert.Equal("0.2.0", loaded.ClientVersion);
            Assert.Equal("device-token-001", loaded.DeviceToken);
            Assert.Equal("0.2.0", reloaded.ClientVersion);
        }
        finally
        {
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
        }
    }

    [Fact]
    public void ClientVersionProvider_ReturnsAssemblyInformationalVersion()
    {
        var version = ClientVersionProvider.CurrentVersion;

        Assert.False(string.IsNullOrWhiteSpace(version));
        Assert.Matches(@"^\d+\.\d+\.\d+", version);
    }
}
