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
}
