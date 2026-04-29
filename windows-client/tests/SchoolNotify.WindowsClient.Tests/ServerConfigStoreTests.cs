using System;
using System.IO;
using System.Threading.Tasks;
using SchoolNotify.WindowsClient.Services;
using Xunit;

namespace SchoolNotify.WindowsClient.Tests;

public sealed class ServerConfigStoreTests
{
    [Fact]
    public async Task ServerConfigStore_ReturnsDefaultBaseUrl_WhenMissing()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-server-config-{Guid.NewGuid():N}.json");
        var store = new ServerConfigStore(filePath);

        var config = await store.LoadAsync();

        Assert.Equal("http://127.0.0.1:8000", config.BaseUrl);
    }

    [Fact]
    public async Task ServerConfigStore_LoadsConfiguredBaseUrl_WhenFileExists()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-server-config-{Guid.NewGuid():N}.json");

        try
        {
            await File.WriteAllTextAsync(filePath, "{" + Environment.NewLine + "  \"BaseUrl\": \"https://www.schoolhelper.cn\"" + Environment.NewLine + "}");
            var store = new ServerConfigStore(filePath);

            var config = await store.LoadAsync();

            Assert.Equal("https://www.schoolhelper.cn", config.BaseUrl);
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
    public async Task ServerConfigStore_LoadsConfiguredBaseUrl_Synchronously_WhenFileExists()
    {
        var filePath = Path.Combine(Path.GetTempPath(), $"school-notify-server-config-{Guid.NewGuid():N}.json");

        try
        {
            await File.WriteAllTextAsync(filePath, "{" + Environment.NewLine + "  \"BaseUrl\": \"http://8.136.61.23:8000\"" + Environment.NewLine + "}");
            var store = new ServerConfigStore(filePath);

            var config = store.Load();

            Assert.Equal("http://8.136.61.23:8000", config.BaseUrl);
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
