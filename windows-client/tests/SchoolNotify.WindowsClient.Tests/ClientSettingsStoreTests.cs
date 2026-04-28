using System;
using System.IO;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Models;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class ClientSettingsStoreTests
{
    [Fact]
    public async Task ClientSettingsStore_ReturnsDefaultAutoStartEnabled_WhenMissing()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-client-settings-{Guid.NewGuid():N}.json");
        var store = new ClientSettingsStore(filePath);

        var settings = await store.LoadAsync();

        Assert.True(settings.AutoStartEnabled);
    }

    [Fact]
    public async Task ClientSettingsStore_RoundTripsDisabledAutoStart()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-client-settings-{Guid.NewGuid():N}.json");

        try
        {
            var store = new ClientSettingsStore(filePath);
            var expected = new ClientSettings(AutoStartEnabled: false);

            await store.SaveAsync(expected);
            var actual = await store.LoadAsync();

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
